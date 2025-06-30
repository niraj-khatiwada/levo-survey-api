from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from src.shared.base_repository import BaseRepository
from src.database.models.response_model import Response
from src.database.models.response_model import ResponseSource
from src.database.db import db
import uuid


class ResponseRepository(BaseRepository[Response]):
    """Repository for Response operations"""

    def __init__(self):
        super().__init__(Response)

    def get_responses_by_survey(
        self, survey_id: str, page: int = 1, per_page: int = 20
    ) -> Dict[str, Any]:
        """Get all responses for a survey (paginated)"""
        query = self.model.query.filter_by(survey_id=uuid.UUID(survey_id))
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

    def get_completed_responses(
        self, survey_id: str, page: int = 1, per_page: int = 20
    ) -> Dict[str, Any]:
        """Get completed responses for a survey (paginated)"""
        query = self.model.query.filter(
            db.and_(
                self.model.survey_id == uuid.UUID(survey_id),
                self.model.created_at.isnot(None),
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

    def get_responses_by_source(
        self, survey_id: str, source: str, page: int = 1, per_page: int = 20
    ) -> Dict[str, Any]:
        """Get responses by source (internal/external)"""
        query = self.model.query.filter_by(
            survey_id=uuid.UUID(survey_id), source=source
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

    def get_responses_by_platform(
        self, survey_id: str, platform: str, page: int = 1, per_page: int = 20
    ) -> Dict[str, Any]:
        """Get responses by external platform"""
        query = self.model.query.filter_by(
            survey_id=uuid.UUID(survey_id), external_platform=platform
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

    def get_response_with_answers(self, response_id: str) -> Optional[Response]:
        """Get response with all its answers"""
        return self.model.query.filter_by(id=uuid.UUID(response_id)).first()

    def get_response_stats(self, survey_id: str) -> Dict[str, Any]:
        """Get response statistics for a survey"""
        total_responses = self.count(survey_id=uuid.UUID(survey_id))
        completed_responses = self.model.query.filter(
            db.and_(
                self.model.survey_id == uuid.UUID(survey_id),
                self.model.created_at.isnot(None),
            )
        ).count()
        internal_responses = self.count(
            survey_id=uuid.UUID(survey_id), source=ResponseSource.INTERNAL
        )
        external_responses = self.count(
            survey_id=uuid.UUID(survey_id), source=ResponseSource.EXTERNAL
        )
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_responses = self.model.query.filter(
            db.and_(
                self.model.survey_id == uuid.UUID(survey_id),
                self.model.created_at >= week_ago,
            )
        ).count()
        return {
            "survey_id": survey_id,
            "total_responses": total_responses,
            "completed_responses": completed_responses,
            "completion_rate": (
                (completed_responses / total_responses * 100)
                if total_responses > 0
                else 0
            ),
            "internal_responses": internal_responses,
            "external_responses": external_responses,
            "recent_responses": recent_responses,
        }

    def get_daily_response_counts(
        self, survey_id: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get daily response counts for the last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        responses = self.model.query.filter(
            db.and_(
                self.model.survey_id == uuid.UUID(survey_id),
                self.model.created_at >= start_date,
            )
        ).all()
        daily_counts = {}
        for response in responses:
            date_str = response.created_at.strftime("%Y-%m-%d")
            daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
        result = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            result.append({"date": date, "count": daily_counts.get(date, 0)})
        return result[::-1]  # Chronological order
