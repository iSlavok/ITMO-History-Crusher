from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import messages
from bot.keyboards import get_public_questions_kb

router = Router(name="public_questions_router")


@router.callback_query(F.data == "public_questions")
@router.message(Command("public_questions"))
async def questions_menu(event: Message | CallbackQuery, state: FSMContext):
    message: Message = event.message if isinstance(event, CallbackQuery) else event
    await message.answer(messages.questions.public_questions_menu, reply_markup=get_public_questions_kb())
    await state.clear()
    if isinstance(event, CallbackQuery):
        await event.answer()
