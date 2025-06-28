from typing import List, Optional
from src.shared.base_repository import BaseRepository
from src.database.models.answer_model import Answer
import uuid


class AnswerRepository(BaseRepository[Answer]):
    """Repository for Answer operations"""

    def __init__(self):
        super().__init__(Answer)

    def get_answers_by_response(self, response_id: str) -> List[Answer]:
        """Get all answers for a response"""
        return self.model.query.filter_by(response_id=uuid.UUID(response_id)).all()

    def get_answers_by_question(self, question_id: str) -> List[Answer]:
        """Get all answers for a question"""
        return self.model.query.filter_by(question_id=uuid.UUID(question_id)).all()
