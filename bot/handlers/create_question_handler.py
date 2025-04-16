from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.enums import UserRole
from bot.filters.role_filter import RoleFilter
from bot.keyboards import get_to_main_kb
from bot.middlewares import ServicesMiddleware
from bot.models import User
from bot.services import QuestionService
from bot.services.exceptions import DateParsingError
from bot.states import CreateQuestion


def get_create_question_router() -> Router:
    router = Router(name="create_question_router")

    router.message.filter(F.chat.type == ChatType.PRIVATE)
    router.message.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))
    router.callback_query.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))
    router.message.middleware.register(ServicesMiddleware())

    @router.callback_query(
        F.data == "create_question",
    )
    async def start(callback: CallbackQuery, state: FSMContext):
        await callback.message.answer("Введите текст вопроса")
        await state.set_state(CreateQuestion.TEXT)
        await callback.answer()

    @router.message(
        F.text.as_("question_text"),
        CreateQuestion.TEXT,
    )
    async def text_input(message: Message, state: FSMContext, question_text: str):
        await message.answer(f"Введите дату для вопроса:\n  {question_text}")
        await state.update_data(create_question_text=question_text)
        await state.set_state(CreateQuestion.ANSWER)

    @router.message(
        F.text.as_("answer_text"),
        CreateQuestion.ANSWER,
        flags={"services": ["question"]},
    )
    async def answer_input(message: Message, state: FSMContext, question_service: QuestionService, user: User,
                           answer_text: str):
        try:
            answer_date = question_service.parse_date_string(answer_text)
        except DateParsingError:
            return await message.answer("Неверный формат даты.")
        data = await state.get_data()
        question_text = data.get("create_question_text")
        question = question_service.create_question(
            user=user,
            text=question_text,
            correct_answer_date=answer_date,
        )
        await message.answer(
            f"Успешно создан ответ <u>{question.correct_answer_date}</u> для вопроса\n"
            f"  {question.text}\n\n"
            f"Вы можете вернуться в главное меню или написать текст следующего вопроса",
            reply_markup=get_to_main_kb(),
        )
        await state.set_state(CreateQuestion.TEXT)

    return router
