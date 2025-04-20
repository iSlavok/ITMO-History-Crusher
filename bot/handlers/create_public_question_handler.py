from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.config import messages
from bot.enums import UserRole
from bot.filters import RoleFilter
from bot.keyboards import get_to_main_kb
from bot.middlewares import ServicesMiddleware
from bot.services import QuestionService
from bot.services.exceptions import DateParsingError
from bot.states import CreatePublicQuestion

router = Router(name="create_public_question_router")

router.message.filter(F.chat.type == ChatType.PRIVATE)
router.message.filter(RoleFilter(UserRole.ADMIN))
router.message.middleware.register(ServicesMiddleware())


@router.message(Command("create_public_question"))
async def start(message: Message, state: FSMContext):
    await message.answer(messages.create_question.question_text_request)
    await state.set_state(CreatePublicQuestion.TEXT)


@router.message(
    F.text.as_("question_text"),
    CreatePublicQuestion.TEXT,
)
async def text_input(message: Message, state: FSMContext, question_text: str):
    await message.answer(messages.create_question.question_date_request.format(question_text=question_text))
    await state.update_data(create_question_text=question_text)
    await state.set_state(CreatePublicQuestion.ANSWER)


@router.message(
    F.text.as_("answer_text"),
    CreatePublicQuestion.ANSWER,
    flags={"services": ["question"]},
)
async def answer_input(message: Message, state: FSMContext, question_service: QuestionService, answer_text: str):
    try:
        answer_date = question_service.parse_date_string(answer_text)
    except DateParsingError:
        return await message.answer(messages.errors.date_parsing_error)
    data = await state.get_data()
    question_text = data.get("create_question_text")
    question_service.create_public_question(text=question_text, correct_answer_date=answer_date)
    await message.answer(messages.create_question.success_created.format(date=answer_date, question_text=question_text),
                         reply_markup=get_to_main_kb())
    await state.set_state(CreatePublicQuestion.TEXT)
