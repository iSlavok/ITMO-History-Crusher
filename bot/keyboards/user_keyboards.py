from typing import Iterable

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_data import DateChoiceCD, SettingAnswerCountCD, EnablePublicQuestions
from bot.config import messages
from bot.schemas import PartialDate

buttons = messages.buttons


def get_main_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text=buttons.test, callback_data="test")
    builder.button(text=buttons.questions, callback_data="questions")
    builder.button(text=buttons.settings, callback_data="settings")
    return builder.adjust(1).as_markup()


def get_to_main_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text=buttons.main, callback_data="main")
    return builder.adjust(1).as_markup()


def get_distractors_kb(distractors: Iterable[PartialDate], answer_id: int, is_public: bool):
    builder = InlineKeyboardBuilder()
    for distractor in distractors:
        builder.button(text=str(distractor), callback_data=DateChoiceCD(answer_id=answer_id, year=distractor.year,
                                                                        month=distractor.month, day=distractor.day,
                                                                        is_public=is_public))
    return builder.adjust(2).as_markup()


def get_settings_kb(enabled_public_questions: bool):
    builder = InlineKeyboardBuilder()
    builder.button(text=buttons.setting_answer_count, callback_data="setting_answer_count")
    if enabled_public_questions:
        builder.button(text=buttons.disable_public_questions, callback_data=EnablePublicQuestions(enable=False))
    else:
        builder.button(text=buttons.enable_public_questions, callback_data=EnablePublicQuestions(enable=True))
    builder.button(text=buttons.main, callback_data="main")
    return builder.adjust(1).as_markup()


def get_to_settings_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text=buttons.settings, callback_data="settings")
    builder.button(text=buttons.main, callback_data="main")
    return builder.adjust(2).as_markup()


def get_settings_answer_count_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="2", callback_data=SettingAnswerCountCD(count=2))
    builder.button(text="4", callback_data=SettingAnswerCountCD(count=4))
    builder.button(text="6", callback_data=SettingAnswerCountCD(count=6))
    builder.button(text="8", callback_data=SettingAnswerCountCD(count=8))
    builder.button(text="10", callback_data=SettingAnswerCountCD(count=10))
    return builder.adjust(5).as_markup()
