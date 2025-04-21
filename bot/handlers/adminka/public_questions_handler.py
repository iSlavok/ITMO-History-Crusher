from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.config import messages
from bot.keyboards import get_public_questions_kb

router = Router(name="public_questions_router")


@router.callback_query(F.data == "public_questions")
async def questions_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(messages.questions.public_questions_menu, reply_markup=get_public_questions_kb())
    await state.clear()
    await callback.answer()
