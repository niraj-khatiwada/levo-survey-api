from datetime import datetime
from src.database.db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Question(db.Model):
    """Question model"""

    __tablename__ = "question"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = db.Column(db.Text, nullable=False)
    required = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    survey_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("survey.id"), nullable=False
    )

    answers = db.relationship(
        "Answer", backref="question", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Question {self.text[:50]}...>"

    def to_dict(self):
        """Convert question to dictionary"""
        return {
            "id": str(self.id),
            "text": self.text,
            "required": self.required,
            "order": self.order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "survey_id": str(self.survey_id),
        }
