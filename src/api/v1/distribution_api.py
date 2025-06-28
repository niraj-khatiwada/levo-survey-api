from flask_smorest import Blueprint
from src.domain.distribution.distribution_service import DistributionService
from src.schema.distribution_schema import (
    DistributionPaginatedSchema,
    CreateBulkDistributionSchema,
    DistributionSchema,
)
from src.shared.schema import PaginationRequestSchema
from injector import inject

distribution_api = Blueprint(
    "distribution_api_v1",
    "distribution_api_v1",
    url_prefix="/api/v1/distribution",
)


@distribution_api.get("/")
@distribution_api.arguments(PaginationRequestSchema, location="query")
@distribution_api.response(200, DistributionPaginatedSchema)
@inject
def query_distributions(query, distribution_service: DistributionService):
    return distribution_service.query_distributions(query=query)


# @distribution_api.get("/<uuid:distribution_id>")
# def get_distribution(distribution_id):
#     distribution = distribution_repo.get_by_id(str(distribution_id))
#     if not distribution:
#         return jsonify({"error": "Distribution not found"}), 404
#     return distribution_schema.jsonify(distribution)


@distribution_api.post("/bulk-distribution")
@distribution_api.arguments(CreateBulkDistributionSchema)
@distribution_api.response(200, DistributionSchema(many=True))
@inject
def create_bulk_distribution(data, distribution_service: DistributionService):
    return distribution_service.create_bulk_distribution(data=data)


# @distribution_api.put("/<uuid:distribution_id>")
# def update_distribution(distribution_id):
#     data = request.get_json()
#     distribution = distribution_repo.update(str(distribution_id), **data)
#     if not distribution:
#         return jsonify({"error": "Distribution not found"}), 404
#     return distribution_schema.jsonify(distribution)


# @distribution_api.delete("/<uuid:distribution_id>")
# def delete_distribution(distribution_id):
#     deleted = distribution_repo.delete(str(distribution_id))
#     if not deleted:
#         return jsonify({"error": "Distribution not found"}), 404
#     return "", 204
