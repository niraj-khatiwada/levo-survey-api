from marshmallow import Schema, fields, validates_schema, ValidationError
from src.database.models.survey_model import SurveyType


class SurveySchema(Schema):
    id = fields.UUID(required=True)
    title = fields.Str(required=True)
    description = fields.Str()
    is_draft = fields.Boolean()
    type = fields.Enum(SurveyType, by_value=True)
    external_url = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class CreateSurveySchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str()
    is_draft = fields.Boolean()
    type = fields.Enum(SurveyType, by_value=True, required=True)
    external_url = fields.Str()

    @validates_schema
    def external_url_required_if(self, data, **_):
        if data.get("type") == SurveyType.EXTERNAL and not data.get("external_url"):
            raise ValidationError(
                {"external_url": "external_url is required when type is EXTERNAL."}
            )
