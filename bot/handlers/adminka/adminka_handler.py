import asyncio
from contextlib import suppress

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import messages
from bot.enums import UserRole
from bot.filters import RoleFilter
from bot.keyboards import get_adminka_kb
from bot.services import UserService

router = Router(name="adminka_router")

router.message.filter(RoleFilter(UserRole.ADMIN))
router.callback_query.filter(RoleFilter(UserRole.ADMIN))


@router.callback_query(F.data == "adminka")
@router.message(Command("adminka"))
async def adminka_menu(event: Message | CallbackQuery, state: FSMContext):
    message: Message = event.message if isinstance(event, CallbackQuery) else event
    await message.answer(messages.adminka.adminka_menu, reply_markup=get_adminka_kb())
    await state.clear()
    if isinstance(event, CallbackQuery):
        await event.answer()


@router.message(
    Command("mailing"),
    F.reply_to_message,
)
async def mailing(message: Message, user_service: UserService):
    total_count = await user_service.get_users_count()
    total_pages = (total_count // 100) + (1 if total_count % 100 > 0 else 0)
    await message.answer("Рассылка начата")
    good = 0
    for page in range(1, total_pages + 1):
        users = await user_service.get_users(page=page, limit=100)
        for user in users:
            with suppress(Exception):
                print(user)
                await message.reply_to_message.send_copy(
                    chat_id=user.id, reply_markup=message.reply_to_message.reply_markup)
                good += 1
            await asyncio.sleep(0.075)
    await message.answer(text=f"Рассылка завершена, её получили {good} чел.")
