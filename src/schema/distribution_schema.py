from marshmallow import Schema, fields
from src.shared.schema import PaginationResponseSchema
from src.database.models.distribution_model import DistributionMethod


class DistributionSchema(Schema):
    id = fields.UUID(required=True)
    method = fields.Enum(DistributionMethod, required=True)
    recipient_email = fields.Str()
    subject = fields.Str()
    message = fields.Str()
    sent_at = fields.DateTime()
    opened_at = fields.DateTime()
    clicked_at = fields.DateTime()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    survey_id = fields.UUID()


class CreateDistributionSchema(Schema):
    method = fields.Enum(DistributionMethod, by_value=True, required=True)
    recipient_email = fields.Email(required=True)
    subject = fields.Str(required=True)
    message = fields.Str(required=True)
    survey_id = fields.UUID(required=True)


class CreateBulkDistributionSchema(Schema):
    recipient_emails = fields.List(fields.Email(), required=True)
    method = fields.Enum(DistributionMethod, required=True)
    subject = fields.Str(required=True)
    message = fields.Str(required=True)
    survey_id = fields.UUID(required=True)


class DistributionPaginatedSchema(PaginationResponseSchema):
    items = fields.List(fields.Nested(DistributionSchema))
