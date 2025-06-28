from flask import request, jsonify
from flask_smorest import Blueprint
from src.domain.question.question_repository import QuestionRepository
from src.domain.question.question_schema import QuestionSchema

questions_api = Blueprint(
    "questions_api_v1",
    "questions_api_v1",
    url_prefix="/api/v1/questions",
)
question_repo = QuestionRepository()
question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)


@questions_api.route("/", methods=["GET"])
def list_questions():
    survey_id = request.args.get("survey_id")
    if not survey_id:
        return jsonify({"error": "survey_id is required"}), 400
    items = question_repo.get_questions_by_survey(survey_id)
    return jsonify(questions_schema.dump(items))


@questions_api.route("/<uuid:question_id>", methods=["GET"])
def get_question(question_id):
    question = question_repo.get_by_id(str(question_id))
    if not question:
        return jsonify({"error": "Question not found"}), 404
    return question_schema.jsonify(question)


@questions_api.route("/", methods=["POST"])
def create_question():
    data = request.get_json()
    errors = question_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    question = question_repo.create(**data)
    return question_schema.jsonify(question), 201


@questions_api.route("/<uuid:question_id>", methods=["PUT"])
def update_question(question_id):
    data = request.get_json()
    question = question_repo.update(str(question_id), **data)
    if not question:
        return jsonify({"error": "Question not found"}), 404
    return question_schema.jsonify(question)


@questions_api.route("/<uuid:question_id>", methods=["DELETE"])
def delete_question(question_id):
    deleted = question_repo.delete(str(question_id))
    if not deleted:
        return jsonify({"error": "Question not found"}), 404
    return "", 204
