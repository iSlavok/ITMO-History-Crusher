from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from bot.repositories import BaseRepository
from bot.models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        statement = (
            select(self.model)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.created_at)
        )
        result = self.session.execute(statement)
        return result.scalars().all()

    def get_users_count(self) -> int:
        statement = (
            select(func.count(self.model.id))
        )
        return self.session.scalar(statement) or 0
