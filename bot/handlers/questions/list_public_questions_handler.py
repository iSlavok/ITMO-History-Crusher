from typing import Sequence

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.callback_data import ListQuestionsPageCD, ListPublicQuestionsPageCD
from bot.config import messages
from bot.keyboards import get_list_public_questions_kb
from bot.models import PublicQuestion
from bot.services import QuestionService

router = Router(name="list_public_questions_router")


@router.callback_query(
    F.data == "list_public_questions",
    flags={"services": ["question"]},
)
@router.message(
    Command("list_public_questions"),
    flags={"services": ["question"]},
)
async def list_public_questions_open(event: Message | CallbackQuery, question_service: QuestionService):
    message: Message = event.message if isinstance(event, CallbackQuery) else event
    public_questions = await question_service.get_public_questions(page=1, limit=10)
    total_count = await question_service.get_public_questions_count()
    total_pages = (total_count // 10) + (1 if total_count % 10 > 0 else 0)
    await message.answer(
        get_question_list_text(public_questions),
        reply_markup=get_list_public_questions_kb(1, total_pages),
    )
    if isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(
    ListPublicQuestionsPageCD.filter(),
    flags={"services": ["question"]},
)
async def list_public_questions_page(callback: CallbackQuery, callback_data: ListQuestionsPageCD,
                                     question_service: QuestionService):
    public_questions = await question_service.get_public_questions(page=callback_data.page, limit=10)
    total_count = await question_service.get_public_questions_count()
    total_pages = (total_count // 10) + (1 if total_count % 10 > 0 else 0)
    await callback.message.edit_text(
        get_question_list_text(public_questions, skip_count=(callback_data.page - 1) * 10),
        reply_markup=get_list_public_questions_kb(callback_data.page, total_pages),
    )
    await callback.answer()


def get_question_list_text(public_questions: Sequence[PublicQuestion], skip_count: int = 0) -> str:
    text = messages.questions.list_public_questions.header + "\n"
    for i, question in enumerate(public_questions, start=1):
        text += "\n" + messages.questions.list_public_questions.question.format(
            question_number=i + skip_count,
            question_id=question.id,
            question_text=question.text,
            question_date=str(question.correct_answer_date),
        )
    return text
