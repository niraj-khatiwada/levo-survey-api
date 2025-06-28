from typing import List, Dict, Any
from src.shared.base_repository import BaseRepository
from src.database.models.question_model import Question
from src.database.db import db
import uuid


class QuestionRepository(BaseRepository[Question]):
    """Repository for Question operations"""

    def __init__(self):
        super().__init__(Question)

    def get_questions_by_survey(
        self, survey_id: str, ordered: bool = True
    ) -> List[Question]:
        """Get all questions for a survey"""
        query = self.model.query.filter_by(survey_id=uuid.UUID(survey_id))
        if ordered:
            query = query.order_by(self.model.order)
        return query.all()

    def get_questions_by_type(
        self, survey_id: str, question_type: str
    ) -> List[Question]:
        """Get questions by type for a specific survey"""
        return (
            self.model.query.filter_by(
                survey_id=uuid.UUID(survey_id), question_type=question_type
            )
            .order_by(self.model.order)
            .all()
        )

    def get_required_questions(self, survey_id: str) -> List[Question]:
        """Get all required questions for a survey"""
        return (
            self.model.query.filter_by(survey_id=uuid.UUID(survey_id), required=True)
            .order_by(self.model.order)
            .all()
        )

    def reorder_questions(
        self, survey_id: str, question_orders: Dict[str, int]
    ) -> bool:
        """Reorder questions for a survey"""
        try:
            for question_id, order in question_orders.items():
                question = self.get_by_id(question_id)
                if question and question.survey_id == uuid.UUID(survey_id):
                    question.order = order
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    def get_question_stats(self, question_id: str) -> Dict[str, Any]:
        """Get statistics for a specific question"""
        question = self.get_by_id(question_id)
        if not question:
            return {}

        # Get all answers for this question
        answers = question.answers.all()

        stats = {
            "question_id": str(question.id),
            "question_text": question.text,
            "question_type": question.question_type,
            "total_answers": len(answers),
            "required": question.required,
            "order": question.order,
        }

        # Add type-specific statistics
        if question.question_type == "multiple_choice":
            stats["options"] = self._get_multiple_choice_stats(answers)
        elif question.question_type == "rating":
            stats["rating_stats"] = self._get_rating_stats(answers)
        elif question.question_type == "checkbox":
            stats["checkbox_stats"] = self._get_checkbox_stats(answers)

        return stats

    def _get_multiple_choice_stats(self, answers) -> Dict[str, int]:
        """Get statistics for multiple choice questions"""
        option_counts = {}
        for answer in answers:
            if answer.value:
                option_counts[answer.value] = option_counts.get(answer.value, 0) + 1
        return option_counts

    def _get_rating_stats(self, answers) -> Dict[str, Any]:
        """Get statistics for rating questions"""
        ratings = [answer.rating for answer in answers if answer.rating is not None]
        if not ratings:
            return {}

        return {
            "average": sum(ratings) / len(ratings),
            "min": min(ratings),
            "max": max(ratings),
            "count": len(ratings),
            "distribution": self._get_rating_distribution(ratings),
        }

    def _get_rating_distribution(self, ratings: List[int]) -> Dict[int, int]:
        """Get distribution of ratings"""
        distribution = {}
        for rating in ratings:
            distribution[rating] = distribution.get(rating, 0) + 1
        return distribution

    def _get_checkbox_stats(self, answers) -> Dict[str, int]:
        """Get statistics for checkbox questions"""
        option_counts = {}
        for answer in answers:
            if answer.values:
                for value in answer.values:
                    option_counts[value] = option_counts.get(value, 0) + 1
        return option_counts
