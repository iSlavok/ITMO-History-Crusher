from typing import Sequence

from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session, aliased

from bot.repositories import BaseRepository
from bot.models import Question, User


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, session: Session):
        super().__init__(session, Question)

    def get_prioritized_questions(self, user: User, high_weight_threshold: float = 8) -> Sequence[Question]:
        question_alias = aliased(self.model)

        question_rank_cte = (
            select(
                question_alias.id.label("question_id"),  # type: ignore
                func.ntile(2).over(
                    order_by=question_alias.updated_at.asc().nullsfirst()  # type: ignore
                ).label("age_group")
            )
            .where(question_alias.user == user)  # type: ignore
            .cte("question_rank_cte")
        )

        statement = (
            select(self.model)
            .join(
                question_rank_cte,
                self.model.id == question_rank_cte.c.question_id
            )
            .where(
                self.model.user == user,
                or_(
                    question_rank_cte.c.age_group == 1,
                    self.model.weight > high_weight_threshold
                )
            )
            .order_by(self.model.id)
        )

        return self.session.scalars(statement).all()
