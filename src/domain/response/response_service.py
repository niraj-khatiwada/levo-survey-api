from injector import inject
from werkzeug.exceptions import NotFound
from uuid import uuid4
from datetime import datetime
from .response_repository import ResponseRepository
from ..question.question_repository import QuestionRepository
from ..survey.survey_repository import SurveyRepository
from ..distribution.distribution_repository import DistributionRepository
from src.database.models.response_model import ResponseSource
from src.database.models.answer_model import Answer
from src.database.models.distribution_model import DistributionStatus
from src.database.db import db
from werkzeug.exceptions import BadRequest


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

        response.completed_at = datetime.utcnow()
        db.session.commit()

        return response
