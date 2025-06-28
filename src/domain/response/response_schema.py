from app import ma
from src.database.models.response_model import Response


class ResponseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Response
        load_instance = True
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")
