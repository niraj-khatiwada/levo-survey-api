from flask_smorest import Blueprint
from injector import inject
from src.domain.response.response_service import ResponseService
from src.schema.response_schema import (
    CreateResponseSchema,
    SubmitAnswersSchema,
    ResponseSchema,
)

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
