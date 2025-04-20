from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_data import ListQuestionsPageCD, DeleteQuestionCD
from bot.config import messages

buttons = messages.buttons


def get_questions_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text=buttons.create_question, callback_data="create_question")
    builder.button(text=buttons.list_questions, callback_data="list_questions")
    builder.button(text=buttons.delete_question, callback_data="delete_question")
    builder.button(text=buttons.main, callback_data="main")
    return builder.adjust(1).as_markup()


def get_to_questions_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text=buttons.back, callback_data="questions")
    builder.button(text=buttons.main, callback_data="main")
    return builder.adjust(2).as_markup()


def get_list_questions_kb(page: int, total_pages: int):
    builder = InlineKeyboardBuilder()
    page_buttons = 0
    if page > 1:
        builder.button(text="◀️", callback_data=ListQuestionsPageCD(page=page - 1))
        page_buttons += 1
    if page < total_pages:
        builder.button(text="▶️", callback_data=ListQuestionsPageCD(page=page + 1))
        page_buttons += 1
    builder.button(text=buttons.back, callback_data="questions")
    builder.button(text=buttons.main, callback_data="main")
    if page_buttons:
        return builder.adjust(page_buttons).as_markup()
    return builder.adjust(2).as_markup()


def get_delete_question_confirm_kb(question_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text=buttons.delete_confirm, callback_data=DeleteQuestionCD(question_id=question_id))
    builder.button(text=buttons.back, callback_data="questions")
    builder.button(text=buttons.main, callback_data="main")
    return builder.adjust(1, 2).as_markup()
