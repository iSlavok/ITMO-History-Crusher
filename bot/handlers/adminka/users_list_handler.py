from typing import Sequence

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.callback_data import UsersListPageCD
from bot.config import messages
from bot.keyboards import get_users_list_kb
from bot.models import User
from bot.services import UserService

router = Router(name="users_list_router")


@router.callback_query(F.data == "users_list")
@router.message(Command(commands=["users_list", "users"]))
async def users_list_open(event: Message | CallbackQuery, user_service: UserService):
    message = event.message if isinstance(event, CallbackQuery) else event
    users = user_service.get_users(page=1, limit=10)
    total_count = user_service.get_users_count()
    total_pages = (total_count // 10) + (1 if total_count % 10 > 0 else 0)
    await message.answer(
        get_users_list_text(users),
        reply_markup=get_users_list_kb(1, total_pages),
    )
    if isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(UsersListPageCD.filter())
async def users_list_page(callback: CallbackQuery, callback_data: UsersListPageCD, user_service: UserService):
    users = user_service.get_users(page=callback_data.page, limit=10)
    total_count = user_service.get_users_count()
    total_pages = (total_count // 10) + (1 if total_count % 10 > 0 else 0)
    await callback.message.edit_text(
        get_users_list_text(users, skip_count=(callback_data.page - 1) * 10),
        reply_markup=get_users_list_kb(callback_data.page, total_pages),
    )
    await callback.answer()


def get_users_list_text(users: Sequence[User], skip_count: int = 0) -> str:
    text = messages.adminka.users_list.header + "\n"
    for i, user in enumerate(users, start=1):
        text += "\n" + messages.adminka.users_list.user.format(
            number=i + skip_count,
            id=user.id,
            username=str(user.username),
            name=user.full_name
        )
    return text
