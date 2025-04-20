from aiogram.fsm.state import StatesGroup, State


class CreatePublicQuestion(StatesGroup):
    TEXT = State()
    ANSWER = State()
