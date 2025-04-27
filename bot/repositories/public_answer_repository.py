from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.models import PublicAnswer
from bot.repositories import BaseRepository


class PublicAnswerRepository(BaseRepository[PublicAnswer]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PublicAnswer)

    async def get_with_question(self, answer_id: int) -> PublicAnswer | None:
        stmt = (
            select(PublicAnswer)
            .where(PublicAnswer.id == answer_id)
            .options(selectinload(PublicAnswer.question))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
