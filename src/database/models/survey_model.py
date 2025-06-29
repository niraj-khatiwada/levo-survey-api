from datetime import datetime
from src.database.db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum


class SurveyType(Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"  # Google Form


class Survey(db.Model):
    """Survey model"""

    __tablename__ = "survey"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_draft = db.Column(db.Boolean, default=False)
    type = db.Column(
        db.Enum(SurveyType, name="survey_type"),
        nullable=False,
        default=SurveyType.INTERNAL,
    )
    external_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    questions = db.relationship(
        "Question", backref="survey", lazy="dynamic", cascade="all, delete-orphan"
    )
    responses = db.relationship(
        "Response", backref="survey", lazy="dynamic", cascade="all, delete-orphan"
    )
    distributions = db.relationship(
        "Distribution", backref="survey", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Survey {self.title}>"

    def to_dict(self):
        """Convert survey to dictionary"""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "is_draft": self.is_draft,
            "type": self.survey_type,
            "external_platform": self.external_platform,
            "external_url": self.external_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "question_count": self.questions.count(),
            "response_count": self.responses.count(),
        }
