from aiogram.fsm.state import StatesGroup, State


class CreateQuestionStates(StatesGroup):
    TEXT = State()
    ANSWER = State()


class DeleteQuestionStates(StatesGroup):
    ID = State()
    CONFIRM = State()


class TestStates(StatesGroup):
    TEXT_ANSWER = State()
    CHOICE_ANSWER = State()
