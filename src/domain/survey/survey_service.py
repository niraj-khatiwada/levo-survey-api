from injector import inject
from .survey_repository import SurveyRepository
from src.schema.survey_schema import CreateSurveySchema


class SurveyService:
    @inject
    def __init__(self, survey_repository: SurveyRepository):
        self.survey_repository = survey_repository

    def create_survey(self, data: CreateSurveySchema):
        """
        Creates a new survey based on given data.
        """
        survey = self.survey_repository.create(**data)
        return survey
