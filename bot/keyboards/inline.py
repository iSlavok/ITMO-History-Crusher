from typing import Iterable

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_data import DateChoiceCD
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
    return builder.adjust(2).as_markup(resize_keyboard=True)
