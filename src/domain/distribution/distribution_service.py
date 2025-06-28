from injector import inject
from werkzeug.exceptions import NotFound
from .distribution_repository import DistributionRepository
from src.decorators import validate_input
from src.shared.schema import PaginationRequestSchema
from src.schema.distribution_schema import CreateBulkDistributionSchema
from ..survey.survey_repository import SurveyRepository
from uuid import uuid4


class DistributionService:
    @inject
    def __init__(
        self,
        distribution_repository: DistributionRepository,
        survey_repository: SurveyRepository,
    ):
        self.distribution_repository = distribution_repository
        self.survey_repository = survey_repository

    @validate_input(PaginationRequestSchema, target="query")
    def query_distributions(self, query: dict):
        """
        Paginated query of the distribution.
        """
        return self.distribution_repository.get_all(**query)

    @validate_input(CreateBulkDistributionSchema)
    def create_bulk_distribution(self, data: dict):
        """
        Creates and distributes the survey content to given recipients.
        """
        survey_exists = self.survey_repository.exists(id=data["survey_id"])
        if not survey_exists:
            raise NotFound("Survey not found")

        recipient_emails = data["recipient_emails"]
        del data["recipient_emails"]
        distributions = self.distribution_repository.bulk_create(
            [
                {"id": uuid4(), "recipient_email": recipient_email, **data}
                for recipient_email in recipient_emails
            ]
        )
        return distributions
