from aiogram import Router, F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.config import messages
from bot.enums import UserRole
from bot.filters import RoleFilter
from bot.keyboards import get_questions_kb

router = Router(name="questions_router")

router.message.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))
router.callback_query.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))


@router.callback_query(F.data == "questions")
async def questions_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(messages.questions.questions_menu, reply_markup=get_questions_kb())
    await state.clear()
    await callback.answer()
