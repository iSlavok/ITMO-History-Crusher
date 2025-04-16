from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.dispatcher.flags import get_flag
from sqlalchemy.orm import Session

from bot.services import QuestionService


class ServicesMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any]
    ) -> Any:
        required = get_flag(data, "services", default=[])
        services = {}
        session: Session = data["session"]
        for service in required:
            if service == "question":
                services["question_service"] = QuestionService(session)
        data.update(services)
        return await handler(event, data)
