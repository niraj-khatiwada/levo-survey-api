from marshmallow import Schema, fields, validate


class DistributionSchema(Schema):
    id = fields.UUID()
    method = fields.Str(required=True)
    recipient_name = fields.Str()
    subject = fields.Str()
    message = fields.Str()
    sent_at = fields.DateTime()
    opened_at = fields.DateTime()
    clicked_at = fields.DateTime()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class DistributionsPaginatedSchema(Schema):
    total = fields.Int()
    data = fields.List(fields.Nested(DistributionSchema))
