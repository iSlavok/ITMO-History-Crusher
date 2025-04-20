from sqlalchemy.orm import Session

from bot.models import PublicQuestion
from bot.repositories import BaseRepository


class PublicQuestionRepository(BaseRepository[PublicQuestion]):
    def __init__(self, session: Session):
        super().__init__(session, PublicQuestion)
