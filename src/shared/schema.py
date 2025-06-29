from marshmallow import Schema, fields, validate


class PaginationRequestSchema(Schema):
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    limit = fields.Integer(load_default=10, validate=validate.Range(min=1, max=200))


class PaginationResponseSchema(Schema):
    # items= pagination.items
    total = fields.Integer()
    pages = fields.Integer()
    current_page = fields.Integer()
    per_page = fields.Integer()
    has_next = fields.Boolean()
    has_prev = fields.Boolean()
