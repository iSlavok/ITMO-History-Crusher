from typing import cast

from aiogram import Router, F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.callback_data import DateChoiceCD
from bot.config import messages
from bot.enums import UserRole, AnswerType
from bot.filters import RoleFilter
from bot.keyboards import get_to_main_kb, get_distractors_kb
from bot.models import User, PublicQuestion, Question
from bot.schemas import PartialDate
from bot.services import QuestionService
from bot.services.exceptions import DateParsingError, QuestionNotFoundError, AnswerNotFoundError
from bot.states import Test

router = Router(name="test_router")

router.message.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))
router.callback_query.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))


@router.callback_query(
    F.data == "test",
    flags={"services": ["question"]},
)
async def start(callback: CallbackQuery, question_service: QuestionService, state: FSMContext, user: User):
    await send_question(message=callback.message, question_service=question_service, state=state, user=user)
    await callback.answer()


@router.message(
    F.text.as_("answer_text"),
    Test.TEXT_ANSWER,
    flags={"services": ["question"]},
)
async def answer_input(message: Message, state: FSMContext, question_service: QuestionService, user: User,
                       answer_text: str):
    data = await state.get_data()
    question_id = data.get("question_id")
    is_public = data.get("is_public")
    try:
        if is_public:
            answer = question_service.submit_user_text_public_answer(question_id=question_id,
                                                                     raw_user_input=answer_text, user=user)
        else:
            answer = question_service.submit_user_text_answer(question_id=question_id, raw_user_input=answer_text)
    except DateParsingError:
        return await message.answer(messages.errors.date_parsing_error)
    except QuestionNotFoundError:
        return await message.answer(messages.errors.question_not_found)
    if answer.type == AnswerType.CORRECT:
        await message.answer(messages.test.correct_text_answer)
        return await send_question(message=message, question_service=question_service, state=state, user=user)
    question = cast(Question | PublicQuestion, answer.question)
    distractors = question_service.generate_distractor_dates(user_date=answer.date,
                                                             correct_date=question.correct_answer_date, user=user)
    await message.answer(messages.test.incorrect_text_answer,
                         reply_markup=get_distractors_kb(distractors, answer_id=answer.id, is_public=is_public))  # type: ignore
    await state.set_state(Test.CHOICE_ANSWER)
    await state.update_data(answer_id=answer.id)


@router.callback_query(
    DateChoiceCD.filter(),
    Test.CHOICE_ANSWER,
    flags={"services": ["question"]},
)
async def answer_choice(callback: CallbackQuery, callback_data: DateChoiceCD, state: FSMContext,
                        question_service: QuestionService, user: User):
    try:
        date = PartialDate(year=callback_data.year, month=callback_data.month, day=callback_data.day)
        if callback_data.is_public:
            answer = question_service.submit_user_choice_public_answer(text_answer_id=callback_data.answer_id,
                                                                       user_date=date)
        else:
            answer = question_service.submit_user_choice_answer(text_answer_id=callback_data.answer_id, user_date=date)
    except DateParsingError:
        return await callback.message.answer(messages.errors.date_parsing_error)
    except QuestionNotFoundError:
        return await callback.message.answer(messages.errors.question_not_found)
    except AnswerNotFoundError:
        return await callback.message.answer(messages.errors.answer_not_found)
    await callback.message.edit_reply_markup(reply_markup=None)
    if answer.type == AnswerType.PART:
        await callback.message.answer(messages.test.correct_choice_answer, reply_markup=get_to_main_kb())
    else:
        question = cast(Question | PublicQuestion, answer.question)
        await callback.message.answer(
            messages.test.incorrect_choice_answer.format(correct_answer=question.correct_answer_date),
            reply_markup=get_to_main_kb())
    return await send_question(message=callback.message, question_service=question_service, state=state, user=user)


async def send_question(message: Message, question_service: QuestionService, state: FSMContext, user: User):
    question = question_service.get_random_question(user)
    if not question:
        return await message.answer(messages.test.question_not_found)
    await message.answer(text=messages.test.question.format(question_text=question.text))
    if isinstance(question, PublicQuestion):
        await state.update_data(question_id=question.id, is_public=True)
    else:
        await state.update_data(question_id=question.id, is_public=False)
    await state.set_state(Test.TEXT_ANSWER)
