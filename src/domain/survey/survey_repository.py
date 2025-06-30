from typing import List, Optional, Dict, Any
from datetime import datetime
from src.shared.base_repository import BaseRepository
from src.database.models.survey_model import Survey
from src.database.db import db
import uuid


class SurveyRepository(BaseRepository[Survey]):
    """Repository for Survey operations"""

    def __init__(self):
        super().__init__(Survey)

    def get_active_surveys(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get all active surveys"""
        query = self.model.query.filter_by(status="active")
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "items": pagination.items,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "per_page": per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }

    def get_surveys_by_type(
        self, survey_type: str, page: int = 1, per_page: int = 20
    ) -> Dict[str, Any]:
        """Get surveys by type (internal/external)"""
        query = self.model.query.filter_by(survey_type=survey_type)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "items": pagination.items,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "per_page": per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }

    def get_surveys_by_platform(
        self, platform: str, page: int = 1, per_page: int = 20
    ) -> Dict[str, Any]:
        """Get surveys by external platform"""
        query = self.model.query.filter_by(external_platform=platform)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "items": pagination.items,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "per_page": per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }

    def search_surveys(
        self, search_term: str, page: int = 1, per_page: int = 20
    ) -> Dict[str, Any]:
        """Search surveys by title or description"""
        query = self.model.query.filter(
            db.or_(
                self.model.title.ilike(f"%{search_term}%"),
                self.model.description.ilike(f"%{search_term}%"),
            )
        )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "items": pagination.items,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "per_page": per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }

    def get_survey_with_questions(self, survey_id: str) -> Optional[Survey]:
        """Get survey with all its questions"""
        return self.model.query.filter_by(id=uuid.UUID(survey_id)).first()

    def get_survey_with_responses(self, survey_id: str) -> Optional[Survey]:
        """Get survey with all its responses"""
        return self.model.query.filter_by(id=uuid.UUID(survey_id)).first()

    def get_survey_stats(self, survey_id: str) -> Dict[str, Any]:
        """Get survey statistics"""
        survey = self.get_by_id(survey_id)
        if not survey:
            return {}

        return {
            "survey_id": str(survey.id),
            "title": survey.title,
            "total_questions": survey.questions.count(),
            "total_responses": survey.responses.count(),
            "response_rate": self._calculate_response_rate(survey),
            "average_completion_time": self._calculate_avg_completion_time(survey),
            "created_at": survey.created_at.isoformat() if survey.created_at else None,
            "last_response_at": self._get_last_response_date(survey),
        }

    def _calculate_response_rate(self, survey: Survey) -> float:
        """Calculate response rate for a survey"""
        total_distributions = survey.distributions.count()
        if total_distributions == 0:
            return 0.0
        return (survey.responses.count() / total_distributions) * 100

    def _calculate_avg_completion_time(self, survey: Survey) -> Optional[float]:
        """Calculate average completion time in minutes"""
        completed_responses = survey.responses.filter(
            db.and_(
                survey.responses.any(completed_at=db.not_(None)),
                survey.responses.any(started_at=db.not_(None)),
            )
        ).all()

        if not completed_responses:
            return None

        total_time = 0
        count = 0
        for response in completed_responses:
            if response.started_at and response.completed_at:
                time_diff = response.completed_at - response.started_at
                total_time += time_diff.total_seconds()
                count += 1

        return (total_time / count) / 60 if count > 0 else None

    def _get_last_response_date(self, survey: Survey) -> Optional[str]:
        """Get the date of the last response"""
        last_response = survey.responses.order_by(
            survey.responses.any(created_at=db.desc())
        ).first()

        return (
            last_response.created_at.isoformat()
            if last_response and last_response.created_at
            else None
        )
