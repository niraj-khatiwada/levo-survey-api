from flask_smorest import Blueprint
from src.domain.survey.survey_service import SurveyService
from src.schema.survey_schema import SurveySchema, CreateSurveySchema
from injector import inject

surveys_api = Blueprint(
    "surveys_api_v1",
    "surveys_api_v1",
    url_prefix="/api/v1/surveys",
)


@surveys_api.post("/")
@surveys_api.arguments(CreateSurveySchema)
@surveys_api.response(200, SurveySchema)
@inject
def create_survey(data, survey_service: SurveyService):
    return survey_service.create_survey(data)
