from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.callback_data import DateChoiceCD
from bot.enums import UserRole, AnswerType
from bot.filters.role_filter import RoleFilter
from bot.keyboards import get_to_main_kb, get_distractors_kb
from bot.middlewares import ServicesMiddleware
from bot.models import User
from bot.schemas import PartialDate
from bot.services import QuestionService
from bot.services.exceptions import DateParsingError, QuestionNotFoundError, AnswerNotFoundError
from bot.states.user_states import Test

router = Router(name="test_router")

router.message.filter(F.chat.type == ChatType.PRIVATE)
router.message.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))
router.callback_query.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))
router.message.middleware.register(ServicesMiddleware())
router.callback_query.middleware.register(ServicesMiddleware())


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
    question_id = int(data.get("question_id"))
    try:
        answer = question_service.submit_user_text_answer(question_id=question_id, raw_user_input=answer_text)
    except DateParsingError:
        return await message.answer("Неверный формат даты.")
    except QuestionNotFoundError:
        return await message.answer("Вопрос не найден.")
    if answer.type == AnswerType.CORRECT:
        await message.answer("Правильный ответ!")
        return await send_question(message=message, question_service=question_service, state=state, user=user)
    distractors = question_service.generate_distractor_dates(answer=answer, user=user)
    await message.answer(
        f"Неправильный ответ.\n"
        f"Попробуйте еще раз, выбрав один из вариантов",
        reply_markup=get_distractors_kb(distractors, answer_id=answer.id)
    )
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
        answer = question_service.submit_user_choice_answer(text_answer_id=callback_data.answer_id, user_date=date)
    except DateParsingError:
        return await callback.message.answer("Неверный формат даты.")
    except QuestionNotFoundError:
        return await callback.message.answer("Вопрос не найден.")
    except AnswerNotFoundError:
        return await callback.message.answer("Ответ не найден.")
    await callback.message.edit_reply_markup(reply_markup=None)
    if answer.type == AnswerType.PART:
        await callback.message.answer("Правильный ответ!", reply_markup=get_to_main_kb())
    else:
        await callback.message.answer("Неправильный ответ.\n"
                                      f"Правильный: {answer.question.correct_answer_date}",
                                      reply_markup=get_to_main_kb())
    return await send_question(message=callback.message, question_service=question_service, state=state, user=user)


async def send_question(message: Message, question_service: QuestionService, state: FSMContext, user: User):
    question = question_service.get_random_question(user)
    if not question:
        return await message.answer("Вопросов нет")
    await message.answer(text=question.text)
    await state.update_data(question_id=question.id)
    await state.set_state(Test.TEXT_ANSWER)
