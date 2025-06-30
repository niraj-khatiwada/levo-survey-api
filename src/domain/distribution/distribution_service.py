from injector import inject
from werkzeug.exceptions import NotFound
from uuid import uuid4
from datetime import datetime
import time
from flask import render_template


from .distribution_repository import DistributionRepository
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

    def query_distributions(self, query: dict):
        """
        Paginated query of the distribution.
        """
        return self.distribution_repository.get_all(**query)

    def get_distributions_by_survey_id(self, survey_id: str):
        """
        Gets all distributions for a given survey
        :param survey_id: ID of the survey
        """
        survey_exists = self.survey_repository.exists(id=survey_id)
        if not survey_exists:
            raise NotFound("Survey not found")

        distributions = self.distribution_repository.get_distributions_by_survey(
            survey_id
        )
        return distributions

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

        # If survey is not draft, schedule the distributions
        if not survey.is_draft:
            self._schedule_distributions(
                distributions, data["subject"], data["message"], survey_id
            )

        return distributions

    def _schedule_distributions(
        self, distributions, subject: str, message: str, survey_id: str
    ):
        """
        Schedules distributions for sending emails
        """
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

    def schedule_existing_distributions_for_survey(self, survey_id: str):
        """
        Schedules all existing distributions for a survey when it's published
        """
        survey = self.survey_repository.get_by_id(str(survey_id))
        if not survey:
            raise NotFound("Survey not found")

        if survey.is_draft:
            raise ValueError("Cannot schedule distributions for a draft survey")

        distributions = self.distribution_repository.get_distributions_by_survey(
            survey_id
        )
        unsent_distributions = [
            d for d in distributions if d.status == DistributionStatus.PENDING
        ]

        for distribution in unsent_distributions:

            if distribution.method.value == DistributionMethod.EMAIL.value:
                subject = distribution.subject
                message = distribution.message

                self.distribute_survey(
                    recipient_email=distribution.recipient_email,
                    subject=subject,
                    message=message,
                    survey_id=survey_id,
                    scheduled_at=distribution.scheduled_at,
                    distribution_id=distribution.id,
                )

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
            survey_url = f"{base_url}/surveys/{survey_id}/take?distribution_id={distribution_id}&clicked_at={int(time.time() * 1000)}"

        html_body = render_template(
            "survey_email.html", message=message, survey_url=survey_url
        )
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

    def increment_distribution_click(self, distribution_id: str):
        distribution = self.distribution_repository.get_by_id(distribution_id)
        if not distribution:
            raise NotFound("Distribution not found")

        distribution.clicked_count = (distribution.clicked_count or 0) + 1
        db.session.commit()
