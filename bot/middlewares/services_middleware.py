from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.dispatcher.flags import get_flag
from sqlalchemy.orm import Session

from bot.repositories import QuestionRepository, AnswerRepository, PublicQuestionRepository, PublicAnswerRepository
from bot.services import QuestionService


class ServicesMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: dict[str, Any]) -> Any:
        required = get_flag(data, "services", default=[])
        services = {}
        session: Session = data["session"]
        for service in required:
            if service == "question":
                question_repo = QuestionRepository(session)
                answer_repo = AnswerRepository(session)
                public_question_repo = PublicQuestionRepository(session)
                public_answer_repo = PublicAnswerRepository(session)
                services["question_service"] = QuestionService(
                    session=session, question_repo=question_repo, answer_repo=answer_repo,
                    public_question_repo=public_question_repo, public_answer_repo=public_answer_repo
                )
        data.update(services)
        return await handler(event, data)
