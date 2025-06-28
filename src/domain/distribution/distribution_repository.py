from typing import List
from src.shared.base_repository import BaseRepository
from src.database.models.distribution_model import Distribution
import uuid


class DistributionRepository(BaseRepository[Distribution]):
    """Repository for Distribution operations"""

    def __init__(self):
        super().__init__(Distribution)

    def get_distributions_by_survey(self, survey_id: str) -> List[Distribution]:
        """Get all distributions for a survey"""
        return self.model.query.filter_by(survey_id=uuid.UUID(survey_id)).all()

    def get_by_recipient_email(self, email: str) -> List[Distribution]:
        """Get all distributions sent to a specific email"""
        return self.model.query.filter_by(recipient_email=email).all()
