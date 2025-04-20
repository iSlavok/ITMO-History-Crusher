from sqlalchemy.orm import Session

from bot.models import PublicAnswer
from bot.repositories import BaseRepository


class PublicAnswerRepository(BaseRepository[PublicAnswer]):
    def __init__(self, session: Session):
        super().__init__(session, PublicAnswer)
