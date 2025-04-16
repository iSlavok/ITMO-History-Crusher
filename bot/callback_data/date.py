from aiogram.filters.callback_data import CallbackData


class DateChoiceCD(CallbackData, prefix='date_choice'):
    answer_id: int
    year: int
    month: int | None
    day: int | None
