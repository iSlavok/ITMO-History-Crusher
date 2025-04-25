from aiogram import Router, F
from aiogram.filters import or_f, Command
from aiogram.types import CallbackQuery, Message

from bot.callback_data import SettingAnswerCountCD, EnablePublicQuestions
from bot.config import messages
from bot.enums import UserRole
from bot.filters import RoleFilter
from bot.keyboards import get_settings_kb, get_settings_answer_count_kb, get_to_settings_kb
from bot.models import User
from bot.services import UserService

router = Router(name="user_settings_router")

router.callback_query.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))


@router.callback_query(F.data == "settings")
@router.message(Command("settings"))
async def open_settings(event: Message | CallbackQuery, user: User):
    message: Message = event.message if isinstance(event, CallbackQuery) else event
    await message.answer(
        messages.settings.settings_menu.format(
            answers_count=user.suggested_answers_count,
            public_status="✅ Включено" if user.enable_public_questions else "❌ Выключено"
        ), reply_markup=get_settings_kb(enabled_public_questions=user.enable_public_questions))
    if isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(F.data == "setting_answer_count")
async def open_answer_count(callback: CallbackQuery):
    await callback.message.answer(messages.settings.answer_count_request, reply_markup=get_settings_answer_count_kb())
    await callback.answer()


@router.callback_query(SettingAnswerCountCD.filter())
async def set_answer_count(callback: CallbackQuery, callback_data: SettingAnswerCountCD, user_service: UserService):
    count = callback_data.count
    await user_service.set_suggested_answers_count(count)
    await callback.message.answer(messages.settings.answer_count_success.format(count=count),
                                  reply_markup=get_to_settings_kb())
    await callback.answer()


@router.callback_query(EnablePublicQuestions.filter())
async def enable_public_questions(callback: CallbackQuery, callback_data: EnablePublicQuestions,
                                  user_service: UserService):
    user = await user_service.set_enable_public_questions(enable=callback_data.enable)
    await callback.message.edit_text(
        messages.settings.settings_menu.format(
            answers_count=user.suggested_answers_count,
            public_status="✅ Включено" if user.enable_public_questions else "❌ Выключено"
        ), reply_markup=get_settings_kb(enabled_public_questions=user.enable_public_questions))
    await callback.answer()
