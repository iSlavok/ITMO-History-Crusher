from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import PublicQuestion
from bot.repositories import BaseRepository


class PublicQuestionRepository(BaseRepository[PublicQuestion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PublicQuestion)

    async def get_public_questions_count(self):
        statement = (
            select(func.count(self.model.id))
        )
        return await self.session.scalar(statement) or 0
