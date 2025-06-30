from flask_smorest import Blueprint
from injector import inject
from src.domain.response.response_service import ResponseService
from src.schema.response_schema import (
    CreateResponseSchema,
    SubmitAnswersSchema,
    ResponseSchema,
)
from src.shared.schema import PaginationRequestSchema
from src.schema.response_schema import SurveyResponsePaginatedSchema


responses_api = Blueprint(
    "responses_api_v1",
    "responses_api_v1",
    url_prefix="/api/v1/responses",
)


@responses_api.post("/")
@responses_api.arguments(CreateResponseSchema)
@responses_api.response(200, ResponseSchema)
@inject
def create_response(data, response_service: ResponseService):
    return response_service.create_response(
        survey_id=data["survey_id"],
        respondent_data=data.get("respondent_data"),
    )


@responses_api.post("/<uuid:response_id>/answers")
@responses_api.arguments(SubmitAnswersSchema)
@responses_api.response(200, ResponseSchema)
@inject
def submit_answers(data, response_id, response_service: ResponseService):
    return response_service.submit_answers(str(response_id), data["answers"])


@responses_api.get("/<uuid:response_id>/answers")
@responses_api.response(200)
@inject
def get_response_answers(response_id, response_service: ResponseService):
    """
    Get all answers for a specific response
    """
    result = response_service.get_response_answers(str(response_id))
    return result


@responses_api.get("/survey/<uuid:survey_id>/responses")
@responses_api.arguments(PaginationRequestSchema, location="query")
@responses_api.response(200, SurveyResponsePaginatedSchema)
@inject
def get_survey_responses(query, survey_id, response_service: ResponseService):
    result = response_service.get_responses_by_survey(str(survey_id), query)
    return result
