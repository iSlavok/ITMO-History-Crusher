from typing import Sequence

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from bot.models import Question, User
from bot.repositories import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Question)

    async def get_prioritized_questions(self, user: User, high_weight_threshold: float = 8) -> Sequence[Question]:
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

        result = await self.session.scalars(statement)
        return result.all()

    async def get_user_questions_paginated_with_answers(self, user: User, skip: int = 0,
                                                        limit: int = 10) -> Sequence[Question]:
        statement = (
            select(self.model)
            .where(self.model.user_id == user.id)
            .options(
                selectinload(self.model.answers)
            )
            .order_by(self.model.id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.scalars(statement)
        return result.all()

    async def get_user_questions_count(self, user: User) -> int:
        statement = (
            select(func.count(self.model.id))
            .where(self.model.user == user)
        )
        return await self.session.scalar(statement) or 0

    async def get_by_id_and_user(self, question_id: int, user: User) -> Question | None:
        statement = (
            select(self.model)
            .where(
                self.model.id == question_id,
                self.model.user == user
            )
        )
        return await self.session.scalar(statement)
