from aiogram.filters.callback_data import CallbackData


class ListQuestionsPageCD(CallbackData, prefix='list_questions_page'):
    page: int


class DeleteQuestionCD(CallbackData, prefix='delete_question'):
    question_id: int
