from marshmallow import Schema, fields, validate, ValidationError


class RespondentDataSchema(Schema):
    name = fields.String(allow_none=True)
    email = fields.String(allow_none=True, validate=validate.Email())
    distribution_id = fields.UUID(allow_none=True)

    def validate_respondent_data(self, data):
        if (
            not data.get("name")
            and not data.get("email")
            and not data.get("distribution_id")
        ):
            raise ValidationError(
                "At least a name or email or distribution_id is required"
            )


class AnswerSchema(Schema):
    question_id = fields.UUID(required=True)
    value = fields.String(allow_none=True)
    values = fields.List(fields.String(), allow_none=True)
    rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=10))
    date_value = fields.Date(allow_none=True)


class CreateResponseSchema(Schema):
    survey_id = fields.UUID(required=True)
    respondent_data = fields.Nested(RespondentDataSchema, required=True)


class SubmitAnswersSchema(Schema):
    answers = fields.List(fields.Nested(AnswerSchema), required=True)


class ResponseSchema(Schema):
    id = fields.UUID()
    respondent_email = fields.String(allow_none=True)
    respondent_name = fields.String(allow_none=True)
    source = fields.String()
    external_response_id = fields.String(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    completed_at = fields.DateTime(allow_none=True)
    survey_id = fields.UUID()
    distribution_id = fields.UUID(allow_none=True)
    answer_count = fields.Integer()
