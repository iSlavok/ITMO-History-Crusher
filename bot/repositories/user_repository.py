from sqlalchemy.orm import Session

from bot.repositories import BaseRepository
from bot.models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)
