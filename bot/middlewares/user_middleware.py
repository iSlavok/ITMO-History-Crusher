from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.database import get_session
from bot.services import UserService


class UserMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: dict[str, Any]) -> Any:
        event_from_user = data["event_from_user"]
        if event_from_user:
            session = next(get_session())
            user_service = UserService(
                session=session,
                user_id=event_from_user.id,
                full_name=event_from_user.full_name,
                username=event_from_user.username,
            )
            data["session"] = session
            data["user_service"] = user_service
            data["user"] = user_service.user
        return await handler(event, data)
