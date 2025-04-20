from aiogram.fsm.state import StatesGroup, State


class CreateQuestion(StatesGroup):
    TEXT = State()
    ANSWER = State()


class DeleteQuestion(StatesGroup):
    ID = State()
    CONFIRM = State()


class Test(StatesGroup):
    TEXT_ANSWER = State()
    CHOICE_ANSWER = State()
