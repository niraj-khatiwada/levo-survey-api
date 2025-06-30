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


@distribution_api.post("/bulk-distribution")
@distribution_api.arguments(CreateBulkDistributionSchema)
@distribution_api.response(200, DistributionSchema(many=True))
@inject
def create_bulk_distribution(data, distribution_service: DistributionService):
    return distribution_service.create_bulk_distribution(data=data)


@distribution_api.get("/by-survey/<uuid:survey_id>")
@distribution_api.response(200, DistributionSchema(many=True))
@inject
def get_distributions_by_survey_id(
    survey_id, distribution_service: DistributionService
):
    return distribution_service.get_distributions_by_survey_id(str(survey_id))


@distribution_api.put("/<uuid:distribution_id>/clicked")
@inject
def increment_distribution_click(
    distribution_id, distribution_service: DistributionService
):
    return distribution_service.increment_distribution_click(str(distribution_id))
