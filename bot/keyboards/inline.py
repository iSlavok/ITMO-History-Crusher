from typing import Iterable

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_data import DateChoiceCD, SettingAnswerCountCD
from bot.schemas import PartialDate


def get_main_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Создать вопрос", callback_data="create_question")
    builder.button(text="Начать тест", callback_data="test")
    builder.button(text="Настройки", callback_data="settings")
    return builder.adjust(1).as_markup()


def get_to_main_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="В главное меню", callback_data="main")
    return builder.adjust(1).as_markup()


def get_distractors_kb(distractors: Iterable[PartialDate], answer_id: int):
    builder = InlineKeyboardBuilder()
    for distractor in distractors:
        builder.button(text=str(distractor), callback_data=DateChoiceCD(answer_id=answer_id, year=distractor.year,
                                                                        month=distractor.month, day=distractor.day))
    return builder.adjust(2).as_markup()


def get_settings_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Изменить кол-во вариантов ответа", callback_data="setting_answer_count")
    builder.button(text="В главное меню", callback_data="main")
    return builder.adjust(1).as_markup()


def get_to_settings_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="В настройки", callback_data="settings")
    builder.button(text="В главное меню", callback_data="main")
    return builder.adjust(2).as_markup()


def get_settings_answer_count_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="2", callback_data=SettingAnswerCountCD(count=2))
    builder.button(text="4", callback_data=SettingAnswerCountCD(count=4))
    builder.button(text="6", callback_data=SettingAnswerCountCD(count=6))
    builder.button(text="8", callback_data=SettingAnswerCountCD(count=8))
    builder.button(text="10", callback_data=SettingAnswerCountCD(count=10))
    return builder.adjust(5).as_markup()
