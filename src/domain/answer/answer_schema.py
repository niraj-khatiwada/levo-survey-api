from app import ma
from src.database.models.answer_model import Answer


class AnswerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Answer
        load_instance = True
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")
