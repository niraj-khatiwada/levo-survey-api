from injector import inject
from werkzeug.exceptions import NotFound
from uuid import uuid4
from .response_repository import ResponseRepository
from ..question.question_repository import QuestionRepository
from ..survey.survey_repository import SurveyRepository
from src.database.models.response_model import ResponseSource
from src.database.models.answer_model import Answer
from src.database.db import db
from werkzeug.exceptions import BadRequest
from src.database.models.distribution_model import DistributionStatus
from src.domain.distribution.distribution_repository import DistributionRepository


class ResponseService:
    @inject
    def __init__(
        self,
        response_repository: ResponseRepository,
        question_repository: QuestionRepository,
        survey_repository: SurveyRepository,
        distribution_repository: DistributionRepository,
    ):
        self.response_repository = response_repository
        self.question_repository = question_repository
        self.survey_repository = survey_repository
        self.distribution_repository = distribution_repository

    def create_response(
        self,
        survey_id: str,
        respondent_data: dict,
    ):
        """
        Creates a new response for a survey
        """
        survey = self.survey_repository.get_by_id(str(survey_id))
        if not survey:
            raise NotFound("Survey not found")

        response_data = {
            "id": uuid4(),
            "survey_id": survey_id,
            "source": ResponseSource.INTERNAL,
        }

        if respondent_data:
            if "distribution_id" in respondent_data:
                response_data["distribution_id"] = str(
                    respondent_data["distribution_id"]
                )
            elif "email" in respondent_data:
                response_data["respondent_email"] = respondent_data["email"]
            elif "name" in respondent_data:
                response_data["respondent_name"] = respondent_data["name"]
            else:
                raise BadRequest("Name is required")

        response = self.response_repository.create(**response_data)

        if "distribution_id" in response_data:
            self.distribution_repository.update(
                str(respondent_data["distribution_id"]),
                status=DistributionStatus.OPENED,
            )

        return response

    def submit_answers(self, response_id: str, answers_data: list):
        """
        Submits answers for a response
        """
        response = self.response_repository.get_by_id(response_id)
        if not response:
            raise NotFound("Response not found")

        answers = []
        for answer_data in answers_data:
            answer = Answer(
                id=uuid4(),
                response_id=response_id,
                question_id=answer_data["question_id"],
                value=answer_data.get("value"),
                values=answer_data.get("values"),
                rating=answer_data.get("rating"),
                date_value=answer_data.get("date_value"),
            )
            answers.append(answer)

        db.session.add_all(answers)
        db.session.commit()

        return response

    def get_responses_by_survey(self, survey_id: str, query: dict):
        """
        Returns paginated responses for a survey.
        """
        result = self.response_repository.get_responses_by_survey(survey_id, **query)
        return result

    def get_response_answers(self, response_id: str):
        """
        Returns all answers for a specific response
        """
        response = self.response_repository.get_by_id(response_id)
        if not response:
            raise NotFound("Response not found")

        answers = db.session.query(Answer).filter_by(response_id=response_id).all()

        questions = self.question_repository.get_questions_by_survey(
            str(response.survey_id)
        )
        question_map = {str(question.id): question for question in questions}

        answer_details = []
        for answer in answers:
            question = question_map.get(str(answer.question_id))
            answer_details.append(
                {
                    "id": str(answer.id),
                    "question_id": str(answer.question_id),
                    "question_text": question.text if question else "Unknown Question",
                    "value": answer.value,
                    "values": answer.values,
                    "rating": answer.rating,
                    "date_value": answer.date_value,
                    "created_at": (
                        answer.created_at.isoformat() if answer.created_at else None
                    ),
                }
            )

        distribution_data = None
        if response.distribution:
            distribution = response.distribution
            distribution_data = {
                "id": str(distribution.id),
                "recipient_method": distribution.method.value,
                "recipient_email": distribution.recipient_email,
                "status": distribution.status.value,
                "scheduled_at": (
                    distribution.scheduled_at.isoformat()
                    if distribution.scheduled_at
                    else None
                ),
                "sent_at": (
                    distribution.sent_at.isoformat() if distribution.sent_at else None
                ),
            }

        return {
            "response_id": response_id,
            "respondent_name": response.respondent_name,
            "respondent_email": response.respondent_email,
            "created_at": (
                response.created_at.isoformat() if response.created_at else None
            ),
            "distribution_id": response.distribution_id,
            "distribution": distribution_data,
            "answers": answer_details,
        }
