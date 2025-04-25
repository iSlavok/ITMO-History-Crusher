from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.repositories import BaseRepository
from bot.models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        statement = (
            select(self.model)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.created_at)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_users_count(self) -> int:
        statement = (
            select(func.count(self.model.id))
        )
        return await self.session.scalar(statement) or 0
