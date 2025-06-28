from injector import inject
from .question_repository import QuestionRepository
from ..survey.survey_repository import SurveyRepository
from werkzeug.exceptions import NotFound
from uuid import uuid4


class QuestionService:
    @inject
    def __init__(
        self,
        question_repository: QuestionRepository,
        survey_repository: SurveyRepository,
    ):
        self.question_repository = question_repository
        self.survey_repository = survey_repository

    def create_question(self, data: dict):
        """
        Adds a new question to a given survey
        """
        survey_exists = self.survey_repository.exists(id=data["survey_id"])
        if not survey_exists:
            raise NotFound("Survey not found")
        question = self.question_repository.create(**data)
        return question

    def create_bulk_questions(self, survey_id: int, questions: list[dict]):
        """
        Adds multiple questions to a given survey
        :param survey_id: ID of the survey
        :param questions: List of dicts, each containing question data
        """
        survey_exists = self.survey_repository.exists(id=survey_id)
        if not survey_exists:
            raise NotFound("Survey not found")

        questions = self.question_repository.bulk_create(
            [
                {"id": uuid4(), "survey_id": survey_id, **question}
                for question in questions
            ]
        )
        return questions
