from injector import singleton
from .domain.survey.survey_repository import SurveyRepository
from .domain.survey.survey_service import SurveyService
from .domain.question.question_repository import QuestionRepository
from .domain.question.question_service import QuestionService
from .domain.distribution.distribution_repository import DistributionRepository
from .domain.distribution.distribution_service import DistributionService
from .services.mail_service import MailService
from .services.scheduler_service import SchedulerService


def bind_modules(binder):
    binder.bind(SurveyRepository, to=SurveyRepository, scope=singleton)
    binder.bind(SurveyService, to=SurveyService, scope=singleton)

    binder.bind(QuestionRepository, to=QuestionRepository, scope=singleton)
    binder.bind(QuestionService, to=QuestionService, scope=singleton)

    binder.bind(DistributionRepository, to=DistributionRepository, scope=singleton)
    binder.bind(DistributionService, to=DistributionService, scope=singleton)

    binder.bind(MailService, to=MailService, scope=singleton)

    binder.bind(SchedulerService, to=SchedulerService, scope=singleton)
