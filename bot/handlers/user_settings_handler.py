from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import or_f
from aiogram.types import CallbackQuery

from bot.callback_data import SettingAnswerCountCD
from bot.config import messages
from bot.enums import UserRole
from bot.filters.role_filter import RoleFilter
from bot.keyboards import get_settings_kb, get_settings_answer_count_kb, get_to_settings_kb
from bot.models import User
from bot.services import UserService

router = Router(name="user_settings_router")

router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))


@router.callback_query(F.data == "settings")
async def open_settings(callback: CallbackQuery, user: User):
    await callback.message.answer(messages.settings.settings_menu.format(answers_count=user.suggested_answers_count),
                                  reply_markup=get_settings_kb())
    await callback.answer()


@router.callback_query(F.data == "setting_answer_count")
async def open_answer_count(callback: CallbackQuery):
    await callback.message.answer(messages.settings.answer_count_request, reply_markup=get_settings_answer_count_kb())
    await callback.answer()


@router.callback_query(SettingAnswerCountCD.filter())
async def set_answer_count(callback: CallbackQuery, callback_data: SettingAnswerCountCD, user_service: UserService):
    count = callback_data.count
    user_service.set_suggested_answers_count(count)
    await callback.message.answer(messages.settings.answer_count_success.format(count=count),
                                  reply_markup=get_to_settings_kb())
    await callback.answer()
