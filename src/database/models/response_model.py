from datetime import datetime
from src.database.db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum


class ResponseSource(Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"


class Response(db.Model):
    """Response model"""

    __tablename__ = "response"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    respondent_email = db.Column(db.String(255))
    respondent_name = db.Column(db.String(255))
    source = db.Column(
        db.Enum(ResponseSource, name="response_source"),
        nullable=False,
        default=ResponseSource.INTERNAL,
    )
    external_response_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    survey_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("survey.id"), nullable=False
    )

    distribution_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("distribution.id"), nullable=True
    )

    answers = db.relationship(
        "Answer", backref="response", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Response {self.id}>"

    def to_dict(self):
        """Convert response to dictionary"""
        return {
            "id": str(self.id),
            "respondent_email": self.respondent_email,
            "respondent_name": self.respondent_name,
            "source": self.source,
            "external_response_id": self.external_response_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "answer_count": self.answers.count(),
            "survey_id": str(self.survey_id),
            "distribution_id": (
                str(self.distribution_id) if self.distribution_id else None
            ),
        }
