from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import PublicAnswer
from bot.repositories import BaseRepository


class PublicAnswerRepository(BaseRepository[PublicAnswer]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PublicAnswer)
