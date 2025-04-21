from typing import Sequence

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.callback_data import ListQuestionsPageCD
from bot.config import messages
from bot.keyboards import get_list_questions_kb
from bot.models import User
from bot.schemas import QuestionInfo
from bot.services import QuestionService

router = Router(name="list_questions_router")


@router.callback_query(
    F.data == "list_questions",
    flags={"services": ["question"]},
)
@router.message(
    Command("create_public_question"),
    flags={"services": ["question"]},
)
async def list_questions_open(event: Message | CallbackQuery, question_service: QuestionService, user: User):
    message: Message = event.message if isinstance(event, CallbackQuery) else event
    questions = question_service.get_questions(user, page=1, limit=10)
    total_count = question_service.get_questions_count(user)
    total_pages = (total_count // 10) + (1 if total_count % 10 > 0 else 0)
    await message.answer(
        get_question_list_text(questions),
        reply_markup=get_list_questions_kb(1, total_pages),
    )
    if isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(
    ListQuestionsPageCD.filter(),
    flags={"services": ["question"]},
)
async def list_questions_page(callback: CallbackQuery, callback_data: ListQuestionsPageCD,
                              question_service: QuestionService, user: User):
    questions = question_service.get_questions(user, page=callback_data.page, limit=10)
    total_count = question_service.get_questions_count(user)
    total_pages = (total_count // 10) + (1 if total_count % 10 > 0 else 0)
    await callback.message.edit_text(
        get_question_list_text(questions, skip_count=(callback_data.page - 1) * 10),
        reply_markup=get_list_questions_kb(callback_data.page, total_pages),
    )
    await callback.answer()


def get_question_list_text(questions: Sequence[QuestionInfo], skip_count: int = 0) -> str:
    text = messages.questions.list_questions.header + "\n"
    for i, question in enumerate(questions, start=1):
        text += "\n" + messages.questions.list_questions.question.format(
            question_number=i + skip_count,
            question_id=question.id,
            answers_score=question.latest_answers_score,
            question_text=question.text,
            question_date=str(question.date),
        )
    return text
