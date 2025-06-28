from app import ma
from src.database.models.survey_model import Survey


class SurveySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Survey
        load_instance = True
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")
