from injector import inject
from flask_smorest import Blueprint
from src.schema.question_schema import (
    QuestionSchema,
    CreateQuestionSchema,
    CreateBulkQuestionSchema,
)
from src.domain.question.question_service import QuestionService

questions_api = Blueprint(
    "questions_api_v1",
    "questions_api_v1",
    url_prefix="/api/v1/questions",
)


@questions_api.post("/")
@questions_api.arguments(CreateQuestionSchema)
@questions_api.response(200, QuestionSchema)
@inject
def create_question(data, question_service: QuestionService):
    return question_service.create_question(data=data)


@questions_api.post("/bulk-questions")
@questions_api.arguments(CreateBulkQuestionSchema)
@questions_api.response(200, QuestionSchema(many=True))
@inject
def bulk_create_question(data, question_service: QuestionService):
    return question_service.create_bulk_questions(
        survey_id=data["survey_id"],
        questions=data["questions"],
    )
