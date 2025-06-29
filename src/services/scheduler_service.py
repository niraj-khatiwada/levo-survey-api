from datetime import datetime
from typing import Optional, Callable
import logging
from app import scheduler

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for handling background job scheduling"""

    def add_job(
        self,
        func: Callable,
        trigger: str = "date",
        run_date: Optional[datetime] = None,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
        job_id: Optional[str] = None,
        replace_existing: bool = True,
        **trigger_args,
    ) -> str:
        """
        Add a job to the scheduler

        Args:
            func: Function to execute
            trigger: Trigger type ('date', 'interval', 'cron')
            run_date: When to run the job (for 'date' trigger)
            args: Arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            job_id: Unique identifier for the job
            replace_existing: Whether to replace existing job with same ID
            **trigger_args: Additional trigger-specific arguments

        Returns:
            str: Job ID
        """
        try:
            job = scheduler.add_job(
                func=func,
                trigger=trigger,
                run_date=run_date,
                args=args,
                kwargs=kwargs,
                id=job_id,
                replace_existing=replace_existing,
                **trigger_args,
            )

            logger.info(f"Job {job.id} scheduled successfully")
            return job.id

        except Exception as e:
            logger.error(f"Failed to schedule job: {str(e)}")
            raise
