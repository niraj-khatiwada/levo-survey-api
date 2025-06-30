from injector import inject
from werkzeug.exceptions import NotFound
from uuid import uuid4
from datetime import datetime, timedelta

from .response_repository import ResponseRepository
from ..question.question_repository import QuestionRepository
from ..survey.survey_repository import SurveyRepository
from src.database.models.response_model import ResponseSource, Response
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
                    "question_type": "unknown",
                    "value": answer.value,
                    "values": answer.values,
                    "rating": answer.rating,
                    "date_value": (
                        answer.date_value.isoformat() if answer.date_value else None
                    ),
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

    def get_survey_analytics(self, survey_id: str):
        """
        Returns comprehensive analytics for a survey
        """
        # Get basic response stats
        response_stats = self.response_repository.get_response_stats(survey_id)

        # Get distribution stats
        distribution_repo = DistributionRepository()
        distributions = distribution_repo.get_distributions_by_survey(survey_id)

        # Calculate distribution stats
        total_distributions = len(distributions)
        sent_distributions = len(
            [d for d in distributions if (d.status == DistributionStatus.SENT)]
        )
        opened_distributions = len(
            [d for d in distributions if d.status == DistributionStatus.OPENED]
        )
        clicked_distributions = sum([d.clicked_count for d in distributions])

        # Get recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_responses = (
            db.session.query(Response)
            .filter(
                db.and_(
                    Response.survey_id == survey_id, Response.created_at >= week_ago
                )
            )
            .count()
        )

        return {
            "survey_id": survey_id,
            "response_stats": response_stats,
            "distribution_stats": {
                "total": total_distributions,
                "sent": sent_distributions,
                "opened": opened_distributions,
                "clicked": clicked_distributions,
                "open_rate": (
                    (opened_distributions / total_distributions * 100)
                    if total_distributions > 0
                    else 0
                ),
                "click_rate": (
                    (clicked_distributions / total_distributions * 100)
                    if total_distributions > 0
                    else 0
                ),
            },
            "recent_activity": {
                "last_7_days": recent_responses,
                "last_24_hours": db.session.query(Response)
                .filter(
                    db.and_(
                        Response.survey_id == survey_id,
                        Response.created_at >= datetime.utcnow() - timedelta(days=1),
                    )
                )
                .count(),
            },
        }

    def get_daily_response_counts(self, survey_id: str, days: int = 30):
        """
        Returns daily response counts for the specified number of days
        """
        return self.response_repository.get_daily_response_counts(survey_id, days)

    def get_question_analytics(self, survey_id: str):
        """
        Returns analytics for each question in the survey
        """
        # Get all questions for the survey
        questions = self.question_repository.get_questions_by_survey(survey_id)

        question_analytics = []
        for question in questions:
            # Get all answers for this question
            answers = (
                db.session.query(Answer)
                .join(Response)
                .filter(
                    db.and_(
                        Response.survey_id == survey_id,
                        Answer.question_id == question.id,
                    )
                )
                .all()
            )

            total_answers = len(answers)
            answered_questions = len(
                [a for a in answers if a.value or a.values or a.rating or a.date_value]
            )
            skipped_questions = total_answers - answered_questions

            # For text questions, get average response length
            avg_response_length = 0
            if len(question.text) and answered_questions > 0:
                text_answers = [a for a in answers if a.value]
                if text_answers:
                    total_length = sum(len(a.value) for a in text_answers if a.value)
                    avg_response_length = total_length / len(text_answers)

            question_analytics.append(
                {
                    "question_id": str(question.id),
                    "question_text": question.text,
                    "question_type": None,
                    "total_responses": total_answers,
                    "answered": answered_questions,
                    "skipped": skipped_questions,
                    "completion_rate": (
                        (answered_questions / total_answers * 100)
                        if total_answers > 0
                        else 0
                    ),
                    "avg_response_length": round(avg_response_length, 1),
                    "avg_rating": None,
                }
            )

        return question_analytics
