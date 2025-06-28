from app import ma
from src.database.models.question_model import Question


class QuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Question
        load_instance = True
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")
