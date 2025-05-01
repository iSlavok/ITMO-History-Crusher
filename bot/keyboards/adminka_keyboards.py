from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_data import UsersListPageCD
from bot.config import messages

buttons = messages.buttons


def get_adminka_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text=buttons.public_questions, callback_data="public_questions")
    builder.button(text=buttons.users_list, callback_data="users_list")
    builder.button(text=buttons.main, callback_data="main")
    return builder.adjust(1).as_markup()


def get_to_adminka_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text=buttons.back, callback_data="adminka")
    builder.button(text=buttons.main, callback_data="main")
    return builder.adjust(1).as_markup()


def get_users_list_kb(page: int, total_pages: int):
    builder = InlineKeyboardBuilder()
    page_buttons = 0
    if page > 1:
        builder.button(text="◀️", callback_data=UsersListPageCD(page=page - 1))
        page_buttons += 1
    if page < total_pages:
        builder.button(text="▶️", callback_data=UsersListPageCD(page=page + 1))
        page_buttons += 1
    builder.button(text=buttons.back, callback_data="adminka")
    builder.button(text=buttons.main, callback_data="main")
    if page_buttons:
        return builder.adjust(page_buttons, 2).as_markup()
    return builder.adjust(2).as_markup()
