from aiogram import Router, F
from aiogram.filters import or_f, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import messages
from bot.enums import UserRole
from bot.filters import RoleFilter
from bot.keyboards import get_main_kb

router = Router(name="user_main_router")

router.message.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))
router.callback_query.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))


@router.message(Command(commands=["start", "main", "cancel"]))
@router.callback_query(F.data.in_({"main", "cancel"}))
async def main(event: Message | CallbackQuery, state: FSMContext):
    message = event.message if isinstance(event, CallbackQuery) else event
    await message.answer(
        text=messages.main_menu,
        reply_markup=get_main_kb(),
    )
    await state.clear()
    if isinstance(event, CallbackQuery):
        await event.answer()
