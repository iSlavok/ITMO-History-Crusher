from aiogram.fsm.state import StatesGroup, State


class CreatePublicQuestionStates(StatesGroup):
    TEXT = State()
    ANSWER = State()


class DeletePublicQuestionStates(StatesGroup):
    ID = State()
    CONFIRM = State()
