from marshmallow import Schema, fields


class QuestionSchema(Schema):
    id = fields.UUID(required=True)
    text = fields.Str(required=True)
    required = fields.Boolean()
    order = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    survey_id = fields.UUID(required=True)


class CreateQuestionSchema(Schema):
    text = fields.Str(required=True)
    required = fields.Boolean()
    order = fields.Integer()
    survey_id = fields.UUID(required=True)


class BulkQuestionsSchema(CreateQuestionSchema):
    class Meta:
        exclude = ("survey_id",)


class CreateBulkQuestionSchema(Schema):
    questions = fields.List(fields.Nested(BulkQuestionsSchema), required=True)
    survey_id = fields.UUID(required=True)
