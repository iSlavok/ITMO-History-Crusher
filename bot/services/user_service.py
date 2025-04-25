from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from bot.repositories import UserRepository
from bot.models import User


class UserService:
    def __init__(self, session: AsyncSession, user_repo: UserRepository):
        self.session = session
        self._user_repo = user_repo
        self._user: User | None = None

    async def get_or_create(self, user_id: int, username: str | None, full_name: str) -> User:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            user = User(
                id=user_id,
                username=username,
                full_name=full_name,
            )
            self._user_repo.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        elif user.username != username or user.full_name != full_name:
            if user.username != username:
                user.username = username
            if user.full_name != full_name:
                user.full_name = full_name
            await self.session.commit()
            await self.session.refresh(user)
        self._user = user
        return user

    @property
    def user(self) -> User:
        return self._user

    async def set_suggested_answers_count(self, count: int) -> User:
        self._user.suggested_answers_count = count
        await self.session.commit()
        await self.session.refresh(self._user)
        return self._user

    async def set_enable_public_questions(self, enable: bool) -> User:
        self._user.enable_public_questions = enable
        await self.session.commit()
        await self.session.refresh(self._user)
        return self._user

    async def get_users(self, page: int = 1, limit: int = 10) -> Sequence[User]:
        if page < 1:
            page = 1
        skip = (page - 1) * limit
        users = await self._user_repo.list_all(skip=skip, limit=limit)
        return users

    async def get_users_count(self) -> int:
        return await self._user_repo.get_users_count()
