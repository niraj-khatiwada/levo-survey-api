from injector import inject
from werkzeug.exceptions import NotFound
from uuid import uuid4
from datetime import datetime

from .distribution_repository import DistributionRepository
from src.decorators import validate_input
from src.shared.schema import PaginationRequestSchema
from src.schema.distribution_schema import CreateBulkDistributionSchema
from ..survey.survey_repository import SurveyRepository
from src.database.models.survey_model import SurveyType
from src.database.models.distribution_model import (
    DistributionStatus,
    DistributionMethod,
)
from src.services.scheduler_service import SchedulerService
from src.services.mail_service import MailService
import logging
from src.database.db import db
from src.config.app_config import AppConfig
from typing import Optional


logger = logging.getLogger(__name__)


class DistributionService:
    @inject
    def __init__(
        self,
        distribution_repository: DistributionRepository,
        survey_repository: SurveyRepository,
        scheduler_service: SchedulerService,
        mail_service: MailService,
    ):
        self.distribution_repository = distribution_repository
        self.survey_repository = survey_repository
        self.scheduler_service = scheduler_service
        self.mail_service = mail_service

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
        survey_id = data["survey_id"]
        survey = self.survey_repository.get_by_id(str(survey_id))
        if not survey:
            raise NotFound("Survey not found")

        recipient_emails = data["recipient_emails"]

        distribution_data = data.copy()
        del distribution_data["recipient_emails"]

        distributions = self.distribution_repository.bulk_create(
            [
                {
                    "id": uuid4(),
                    "recipient_email": recipient_email,
                    **distribution_data,
                }
                for recipient_email in recipient_emails
            ]
        )

        if survey.is_draft:
            return distributions

        # TODO add a new function to send distribution when is_draft is set to false
        subject = data["subject"]
        message = data["message"]

        for distribution in distributions:
            if distribution.method.value == DistributionMethod.EMAIL.value:
                # Send emails in background for each recipient
                self.distribute_survey(
                    recipient_email=distribution.recipient_email,
                    subject=subject,
                    message=message,
                    survey_id=survey_id,
                    scheduled_at=distribution.scheduled_at,
                    distribution_id=distribution.id,
                )
        return distributions

    def distribute_survey(
        self,
        recipient_email: str,
        subject: str,
        message: str,
        survey_id: str,
        distribution_id: str,
        scheduled_at: Optional[datetime] = None,
    ) -> str:
        """
        Distribute a survey email in background.

        Args:
            recipient_email: Recipient email address
            subject: Email subject
            message: Email message content
            survey_id: Id of the survey

        Returns:
            str: Job ID for the scheduled email
        """
        survey = self.survey_repository.get_by_id(str(survey_id))

        if survey.type == SurveyType.EXTERNAL and survey.external_url:
            survey_url = survey.external_url
        else:

            base_url = AppConfig.CLIENT_URL
            print(">>", base_url)
            survey_url = f"{base_url}/survey/{survey_id}"

        html_body = f"""
        <html>
            <body>
                <h2>{subject}</h2>
                <p>{message}</p>
                <p>Please click the link below to access the survey:</p>
                <p><a href="{survey_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Take Survey</a></p>
                <p>Or copy and paste this link in your browser: <a href="{survey_url}">{survey_url}</a></p>
                <br>
                <p>Thank you for your participation!</p>
            </body>
        </html>
        """
        plain_body = f"{message}\n\nSurvey Link: {survey_url}"

        return self.scheduler_service.add_job(
            func=self.send_survey_email,
            trigger="date",
            run_date=scheduled_at,
            args=[recipient_email, subject, plain_body, html_body, distribution_id],
        )

    def send_survey_email(
        self,
        recipient_email: str,
        subject: str,
        plain_body: str,
        html_body: str,
        distribution_id: str,
    ):
        from server import app

        with app.app_context():
            # In case of scheduled, distribution might be deleted at this point. So make sure to check first.
            distribution = self.distribution_repository.get_by_id(
                (str(distribution_id))
            )
            if not distribution:
                logger.fatal(
                    f"Distribution of id='{distribution_id}' is missing. Halting sending scheduled email."
                )
                return

            self.mail_service.send_email(
                to_emails=[recipient_email],
                subject=subject,
                body=plain_body,
                html_body=html_body,
            )
            distribution.sent = True
            distribution.status = DistributionStatus.SENT.name
            distribution.sent_at = datetime.utcnow()
            db.session.commit()
