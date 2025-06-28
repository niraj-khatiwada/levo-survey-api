from flask import request, jsonify
from flask_smorest import Blueprint
from src.domain.survey.survey_repository import SurveyRepository
from src.domain.survey.survey_schema import SurveySchema

surveys_api = Blueprint(
    "surveys_api_v1",
    "surveys_api_v1",
    url_prefix="/api/v1/surveys",
)
survey_repo = SurveyRepository()
survey_schema = SurveySchema()
surveys_schema = SurveySchema(many=True)


@surveys_api.route("/", methods=["GET"])
def list_surveys():
    """List all surveys (paginated)"""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    result = survey_repo.get_all(page=page, per_page=per_page)
    return jsonify(
        {
            "items": surveys_schema.dump(result["items"]),
            "total": result["total"],
            "pages": result["pages"],
            "current_page": result["current_page"],
            "per_page": result["per_page"],
            "has_next": result["has_next"],
            "has_prev": result["has_prev"],
        }
    )


@surveys_api.route("/<uuid:survey_id>", methods=["GET"])
def get_survey(survey_id):
    survey = survey_repo.get_by_id(str(survey_id))
    if not survey:
        return jsonify({"error": "Survey not found"}), 404
    return survey_schema.jsonify(survey)


@surveys_api.route("/", methods=["POST"])
def create_survey():
    data = request.get_json()
    errors = survey_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    survey = survey_repo.create(**data)
    return survey_schema.jsonify(survey), 201


@surveys_api.route("/<uuid:survey_id>", methods=["PUT"])
def update_survey(survey_id):
    data = request.get_json()
    survey = survey_repo.update(str(survey_id), **data)
    if not survey:
        return jsonify({"error": "Survey not found"}), 404
    return survey_schema.jsonify(survey)


@surveys_api.route("/<uuid:survey_id>", methods=["DELETE"])
def delete_survey(survey_id):
    deleted = survey_repo.delete(str(survey_id))
    if not deleted:
        return jsonify({"error": "Survey not found"}), 404
    return "", 204
