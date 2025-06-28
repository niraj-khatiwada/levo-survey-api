from datetime import datetime
from src.database.db import db
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


class Answer(db.Model):
    """Answer model"""

    __tablename__ = "answer"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    value = db.Column(db.Text)  # For text, single choice answers
    values = db.Column(JSON)  # For multiple choice, checkbox answers
    rating = db.Column(db.Integer)  # For rating questions
    date_value = db.Column(db.Date)  # For date questions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    response_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("response.id"), nullable=False
    )
    question_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("question.id"), nullable=False
    )

    def __repr__(self):
        return f"<Answer {self.id}>"

    def to_dict(self):
        """Convert answer to dictionary"""
        return {
            "id": str(self.id),
            "value": self.value,
            "values": self.values,
            "rating": self.rating,
            "date_value": self.date_value.isoformat() if self.date_value else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "response_id": str(self.response_id),
            "question_id": str(self.question_id),
        }
