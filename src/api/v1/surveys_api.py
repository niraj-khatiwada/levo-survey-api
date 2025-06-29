from flask_smorest import Blueprint
from injector import inject
from src.domain.survey.survey_service import SurveyService
from src.schema.survey_schema import (
    SurveySchema,
    CreateSurveySchema,
    SurveyPaginatedSchema,
)
from src.shared.schema import PaginationRequestSchema


surveys_api = Blueprint(
    "surveys_api_v1",
    "surveys_api_v1",
    url_prefix="/api/v1/surveys",
)


@surveys_api.get("/")
@surveys_api.arguments(PaginationRequestSchema, location="query")
@surveys_api.response(200, SurveyPaginatedSchema)
@inject
def query_surveys(query, survey_service: SurveyService):
    return survey_service.query_surveys(query=query)


@surveys_api.get("/<uuid:survey_id>")
@surveys_api.response(200, SurveySchema)
@inject
def get_survey_by_id(survey_id, survey_service: SurveyService):
    return survey_service.get_survey_by_id(str(survey_id))


@surveys_api.post("/<uuid:survey_id>/publish")
@surveys_api.response(200, SurveySchema)
@inject
def publish_survey(survey_id, survey_service: SurveyService):
    return survey_service.publish_survey(str(survey_id))


@surveys_api.post("/")
@surveys_api.arguments(CreateSurveySchema)
@surveys_api.response(200, SurveySchema)
@inject
def create_survey(data, survey_service: SurveyService):
    return survey_service.create_survey(data)
