from sqlalchemy import select, func
from sqlalchemy.orm import Session

from bot.enums import AnswerType
from bot.repositories import BaseRepository
from bot.models import Answer


class AnswerRepository(BaseRepository[Answer]):
    def __init__(self, session: Session):
        super().__init__(session, Answer)

    def get_answer_counts_for_weight(self, question_id: int, history_limit: int) -> tuple[list[AnswerType], int]:
        stmt_last_answers = (
            select(Answer.type)
            .where(Answer.question_id == question_id)
            .order_by(Answer.created_at.desc())
            .limit(history_limit)
        )

        stmt_total_count = (
            select(func.count(Answer.id))
            .where(Answer.question_id == question_id)
        )

        last_answer_types = self.session.scalars(stmt_last_answers).all()
        total_answers_count = self.session.scalar(stmt_total_count)

        if total_answers_count is None:
            total_answers_count = 0

        return list(last_answer_types), total_answers_count
