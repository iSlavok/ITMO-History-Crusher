from aiogram.fsm.state import StatesGroup, State


class CreatePublicQuestion(StatesGroup):
    TEXT = State()
    ANSWER = State()


class DeletePublicQuestion(StatesGroup):
    ID = State()
    CONFIRM = State()
