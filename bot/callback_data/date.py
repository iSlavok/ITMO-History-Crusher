from aiogram.filters.callback_data import CallbackData


class DateChoiceCD(CallbackData, prefix="date_choice"):
    answer_id: int
    is_public: bool
    year: int
    month: int | None
    day: int | None


class SettingAnswerCountCD(CallbackData, prefix="setting_answer_count"):
    count: int
