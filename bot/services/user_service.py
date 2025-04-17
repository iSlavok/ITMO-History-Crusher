from sqlalchemy.orm import Session

from bot.repositories import UserRepository
from bot.models import User


class UserService:
    def __init__(self, session: Session, user_id: int, full_name: str, username: str | None):
        self.session = session
        self._user_repo = UserRepository(session)
        self._user: User = self._get_or_create(user_id, username, full_name)

    def _get_or_create(self, user_id: int, username: str | None, full_name: str) -> User:
        user = self._user_repo.get_by_id(user_id)
        if user:
            if user.username != username:
                user.username = username
            if user.full_name != full_name:
                user.full_name = full_name
            self.session.commit()
            self.session.refresh(user)
            return user
        user = User(
            id=user_id,
            username=username,
            full_name=full_name,
        )
        self._user_repo.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    @property
    def user(self) -> User:
        return self._user

    def set_suggested_answers_count(self, count: int) -> User:
        self._user.suggested_answers_count = count
        self.session.commit()
        self.session.refresh(self._user)
        return self._user

