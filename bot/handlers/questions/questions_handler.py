from aiogram import Router, F
from aiogram.filters import or_f, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import messages
from bot.enums import UserRole
from bot.filters import RoleFilter
from bot.keyboards import get_questions_kb

router = Router(name="questions_router")

router.message.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))
router.callback_query.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))


@router.callback_query(F.data == "questions")
@router.message(Command("questions"))
async def questions_menu(event: Message | CallbackQuery, state: FSMContext):
    message: Message = event.message if isinstance(event, CallbackQuery) else event
    await message.answer(messages.questions.questions_menu, reply_markup=get_questions_kb())
    await state.clear()
    if isinstance(event, CallbackQuery):
        await event.answer()
