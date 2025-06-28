from injector import singleton
from .survey.survey_repository import SurveyRepository
from .survey.survey_service import SurveyService
from .question.question_repository import QuestionRepository
from .question.question_service import QuestionService
from .distribution.distribution_repository import DistributionRepository
from .distribution.distribution_service import DistributionService


def bind_modules(binder):
    binder.bind(SurveyRepository, to=SurveyRepository, scope=singleton)
    binder.bind(SurveyService, to=SurveyService, scope=singleton)

    binder.bind(QuestionRepository, to=QuestionRepository, scope=singleton)
    binder.bind(QuestionService, to=QuestionService, scope=singleton)

    binder.bind(DistributionRepository, to=DistributionRepository, scope=singleton)
    binder.bind(DistributionService, to=DistributionService, scope=singleton)
