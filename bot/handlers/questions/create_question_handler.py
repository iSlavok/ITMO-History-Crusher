from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import messages
from bot.keyboards import get_to_questions_kb
from bot.models import User
from bot.services import QuestionService
from bot.services.exceptions import DateParsingError
from bot.states import CreateQuestionStates

router = Router(name="create_question_router")


@router.callback_query(F.data == "create_question")
@router.message(Command("create_question"))
async def start(event: Message | CallbackQuery, state: FSMContext):
    message: Message = event.message if isinstance(event, CallbackQuery) else event
    await message.answer(messages.questions.create_question.question_text_request,
                         reply_markup=get_to_questions_kb())
    await state.set_state(CreateQuestionStates.TEXT)
    if isinstance(event, CallbackQuery):
        await event.answer()


@router.message(
    F.text.as_("question_text"),
    CreateQuestionStates.TEXT,
)
async def text_input(message: Message, state: FSMContext, question_text: str):
    await message.answer(messages.questions.create_question.question_date_request.format(question_text=question_text))
    await state.update_data(create_question_text=question_text)
    await state.set_state(CreateQuestionStates.ANSWER)


@router.message(
    F.text.as_("answer_text"),
    CreateQuestionStates.ANSWER,
    flags={"services": ["question"]},
)
async def answer_input(message: Message, state: FSMContext, question_service: QuestionService, user: User,
                       answer_text: str):
    try:
        answer_date = question_service.parse_date_string(answer_text)
    except DateParsingError:
        return await message.answer(messages.errors.date_parsing_error)
    data = await state.get_data()
    question_text = data.get("create_question_text")
    await question_service.create_question(user=user, text=question_text, correct_answer_date=answer_date)
    await message.answer(
        messages.questions.create_question.success_created.format(date=answer_date, question_text=question_text),
        reply_markup=get_to_questions_kb())
    await state.set_state(CreateQuestionStates.TEXT)
    return None
