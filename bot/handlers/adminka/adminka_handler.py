from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import messages
from bot.enums import UserRole
from bot.filters import RoleFilter
from bot.keyboards import get_adminka_kb

router = Router(name="adminka_router")

router.message.filter(RoleFilter(UserRole.ADMIN))
router.callback_query.filter(RoleFilter(UserRole.ADMIN))


@router.callback_query(F.data == "adminka")
@router.message(Command("adminka"))
async def adminka_menu(event: Message | CallbackQuery, state: FSMContext):
    message = event.message if isinstance(event, CallbackQuery) else event
    await message.answer(messages.adminka.adminka_menu, reply_markup=get_adminka_kb())
    await state.clear()
    if isinstance(event, CallbackQuery):
        await event.answer()
