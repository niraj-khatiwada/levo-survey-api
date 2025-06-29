from datetime import datetime
from src.database.db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum


class DistributionMethod(Enum):
    EMAIL = "email"
    LINK = "link"
    EXTERNAL = "external"


class DistributionStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    OPENED = "opened"
    CLICKED = "clicked"
    FAILED = "failed"


class Distribution(db.Model):
    """Distribution model"""

    __tablename__ = "distribution"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    method = db.Column(
        db.Enum(DistributionMethod, name="distribution_method"),
        nullable=False,
        default=DistributionMethod.LINK,
    )
    recipient_email = db.Column(db.String(255))
    subject = db.Column(db.String(255))
    scheduled_at = db.Column(db.DateTime)
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)
    opened_at = db.Column(db.DateTime)
    clicked_at = db.Column(db.DateTime)
    status = db.Column(
        db.Enum(DistributionStatus, name="distribution_status"),
        nullable=False,
        default=DistributionStatus.PENDING,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    survey_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("survey.id"), nullable=False
    )

    def __repr__(self):
        return f"<Distribution {self.method} to {self.recipient_email}>"

    def to_dict(self):
        """Convert distribution to dictionary"""
        return {
            "id": str(self.id),
            "method": self.method,
            "recipient_email": self.recipient_email,
            "subject": self.subject,
            "message": self.message,
            "scheduled_at": (
                self.scheduled_at.isoformat() if self.scheduled_at else None
            ),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "clicked_at": self.clicked_at.isoformat() if self.clicked_at else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "survey_id": str(self.survey_id),
        }
