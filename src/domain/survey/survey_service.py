from injector import inject
from .survey_repository import SurveyRepository
from src.shared.schema import PaginationRequestSchema
from src.schema.survey_schema import CreateSurveySchema
from src.decorators import validate_input
from werkzeug.exceptions import NotFound
from src.domain.distribution.distribution_service import DistributionService
import logging

logger = logging.getLogger(__name__)


class SurveyService:
    @inject
    def __init__(
        self,
        survey_repository: SurveyRepository,
        distribution_service: DistributionService,
    ):
        self.survey_repository = survey_repository
        self.distribution_service = distribution_service

    @validate_input(PaginationRequestSchema, target="query")
    def query_surveys(self, query: dict):
        """
        Paginated query of the survey.
        """
        return self.survey_repository.get_all(**query)

    def get_survey_by_id(self, survey_id: str):
        """
        Gets a survey by its ID.
        """
        survey = self.survey_repository.get_by_id(survey_id)
        if not survey:
            raise NotFound("Survey not found")
        return survey

    def publish_survey(self, survey_id: str):
        """
        Publishes a survey by setting is_draft to False and scheduling existing distributions
        """
        survey = self.survey_repository.get_by_id(survey_id)
        if not survey:
            raise NotFound("Survey not found")

        if not survey.is_draft:
            raise ValueError("Survey is already published")

        survey.is_draft = False
        self.survey_repository.update(survey_id, is_draft=False)
        self.distribution_service.schedule_existing_distributions_for_survey(survey_id)
        return survey

    def create_survey(self, data: CreateSurveySchema):
        """
        Creates a new survey based on given data.
        """
        survey = self.survey_repository.create(**data)
        return survey
