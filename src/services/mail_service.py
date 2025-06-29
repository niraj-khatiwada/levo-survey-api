from flask_mail import Message
from typing import List, Optional
import logging
from app import mail
from src.config.mail_config import MailConfig

logger = logging.getLogger(__name__)


class MailService:
    """Service for handling email operations"""

    def send_email(
        self,
        to_emails: List,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        sender: Optional[str] = None,
    ):
        """
        Send an email immediately

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Plain text email body
            html_body: HTML email body (optional)
            sender: Sender email address (optional, uses default if not provided)
        """
        from server import app

        with app.app_context():
            msg = Message(
                subject=subject,
                recipients=to_emails,
                body=body,
                html=html_body,
                sender=sender or MailConfig.MAIL_DEFAULT_SENDER,
            )
            mail.send(msg)
