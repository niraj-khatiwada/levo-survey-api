from flask import request, jsonify
from flask_smorest import Blueprint
from src.domain.distribution.distribution_repository import DistributionRepository
from src.domain.distribution.distribution_schema import DistributionSchema
from src.shared.schema import PaginationRequestSchema

distribution_api = Blueprint(
    "distribution_api_v1",
    "distribution_api_v1",
    url_prefix="/api/v1/distribution",
)
distribution_repo = DistributionRepository()
distribution_schema = DistributionSchema()
distributions_schema = DistributionSchema(many=True)


@distribution_api.arguments(PaginationRequestSchema, location="query")
# @distribution_api.response(200, DistributionsPaginatedSchema)
@distribution_api.get("/")
def list_distributions():
    survey_id = request.args.get("survey_id")
    if not survey_id:
        return jsonify({"error": "survey_id is required"}), 400
    items = distribution_repo.filter_by(survey_id=survey_id)
    return jsonify(distributions_schema.dump(items))


@distribution_api.get("/<uuid:distribution_id>")
def get_distribution(distribution_id):
    distribution = distribution_repo.get_by_id(str(distribution_id))
    if not distribution:
        return jsonify({"error": "Distribution not found"}), 404
    return distribution_schema.jsonify(distribution)


@distribution_api.post("/")
def create_distribution():
    data = request.get_json()
    errors = distribution_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    distribution = distribution_repo.create(**data)
    return distribution_schema.jsonify(distribution), 201


@distribution_api.put("/<uuid:distribution_id>")
def update_distribution(distribution_id):
    data = request.get_json()
    distribution = distribution_repo.update(str(distribution_id), **data)
    if not distribution:
        return jsonify({"error": "Distribution not found"}), 404
    return distribution_schema.jsonify(distribution)


@distribution_api.delete("/<uuid:distribution_id>")
def delete_distribution(distribution_id):
    deleted = distribution_repo.delete(str(distribution_id))
    if not deleted:
        return jsonify({"error": "Distribution not found"}), 404
    return "", 204
