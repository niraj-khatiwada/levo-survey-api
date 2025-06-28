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


# @questions_api.route("/", methods=["GET"])
# def list_questions():
#     survey_id = request.args.get("survey_id")
#     if not survey_id:
#         return jsonify({"error": "survey_id is required"}), 400
#     items = question_repo.get_questions_by_survey(survey_id)
#     return jsonify(questions_schema.dump(items))


# @questions_api.route("/<uuid:question_id>", methods=["GET"])
# def get_question(question_id):
#     question = question_repo.get_by_id(str(question_id))
#     if not question:
#         return jsonify({"error": "Question not found"}), 404
#     return question_schema.jsonify(question)


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


# @questions_api.route("/<uuid:question_id>", methods=["PUT"])
# def update_question(question_id):
#     data = request.get_json()
#     question = question_repo.update(str(question_id), **data)
#     if not question:
#         return jsonify({"error": "Question not found"}), 404
#     return question_schema.jsonify(question)


# @questions_api.route("/<uuid:question_id>", methods=["DELETE"])
# def delete_question(question_id):
#     deleted = question_repo.delete(str(question_id))
#     if not deleted:
#         return jsonify({"error": "Question not found"}), 404
#     return "", 204
