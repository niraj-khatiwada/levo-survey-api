from flask import request, jsonify
from flask_smorest import Blueprint
from src.domain.response.response_repository import ResponseRepository
from src.domain.response.response_schema import ResponseSchema

responses_api = Blueprint(
    "responses_api_v1",
    "responses_api_v1",
    url_prefix="/api/v1/responses",
)
response_repo = ResponseRepository()
response_schema = ResponseSchema()
responses_schema = ResponseSchema(many=True)


@responses_api.route("/", methods=["GET"])
def list_responses():
    survey_id = request.args.get("survey_id")
    if not survey_id:
        return jsonify({"error": "survey_id is required"}), 400
    result = response_repo.get_responses_by_survey(survey_id)
    return jsonify(
        {
            "items": responses_schema.dump(result["items"]),
            "total": result["total"],
            "pages": result["pages"],
            "current_page": result["current_page"],
            "per_page": result["per_page"],
            "has_next": result["has_next"],
            "has_prev": result["has_prev"],
        }
    )


@responses_api.route("/<uuid:response_id>", methods=["GET"])
def get_response(response_id):
    response = response_repo.get_by_id(str(response_id))
    if not response:
        return jsonify({"error": "Response not found"}), 404
    return response_schema.jsonify(response)


@responses_api.route("/", methods=["POST"])
def create_response():
    data = request.get_json()
    errors = response_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    response = response_repo.create(**data)
    return response_schema.jsonify(response), 201


@responses_api.route("/<uuid:response_id>", methods=["PUT"])
def update_response(response_id):
    data = request.get_json()
    response = response_repo.update(str(response_id), **data)
    if not response:
        return jsonify({"error": "Response not found"}), 404
    return response_schema.jsonify(response)


@responses_api.route("/<uuid:response_id>", methods=["DELETE"])
def delete_response(response_id):
    deleted = response_repo.delete(str(response_id))
    if not deleted:
        return jsonify({"error": "Response not found"}), 404
    return "", 204
