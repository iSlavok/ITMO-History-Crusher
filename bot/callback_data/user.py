from aiogram.filters.callback_data import CallbackData


class EnablePublicQuestions(CallbackData, prefix="enable_public_questions"):
    enable: bool
