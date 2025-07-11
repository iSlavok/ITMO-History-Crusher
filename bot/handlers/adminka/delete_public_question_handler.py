from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.callback_data import DeletePublicQuestionCD
from bot.config import messages
from bot.keyboards import get_to_public_questions_kb, get_delete_public_question_confirm_kb
from bot.services import QuestionService
from bot.services.exceptions import QuestionNotFoundError
from bot.states import DeletePublicQuestionStates

router = Router(name="delete_public_question_router")


@router.callback_query(F.data == "delete_public_question")
@router.message(Command("delete_public_question"))
async def delete_question_id_request(event: Message | CallbackQuery, state: FSMContext):
    message: Message = event.message if isinstance(event, CallbackQuery) else event
    await message.answer(messages.questions.delete_public_question.id_request,
                         reply_markup=get_to_public_questions_kb())
    await state.set_state(DeletePublicQuestionStates.ID)
    if isinstance(event, CallbackQuery):
        await event.answer()


@router.message(
    F.text.func(int).as_("question_id"),
    DeletePublicQuestionStates.ID,
    flags={"services": ["question"]},
)
async def delete_question_id(message: Message, state: FSMContext, question_id: int, question_service: QuestionService):
    try:
        question = await question_service.get_public_question_by_id(question_id)
    except QuestionNotFoundError:
        return await message.answer(messages.errors.question_not_found)
    await message.answer(messages.questions.delete_public_question.delete_confirm.format(question_text=question.text),
                         reply_markup=get_delete_public_question_confirm_kb(question.id))
    await state.set_state(DeletePublicQuestionStates.CONFIRM)
    return None


@router.callback_query(
    DeletePublicQuestionCD.filter(),
    DeletePublicQuestionStates.CONFIRM,
    flags={"services": ["question"]},
)
async def delete_question_confirm(callback: CallbackQuery, callback_data: DeletePublicQuestionCD, state: FSMContext,
                                  question_service: QuestionService):
    question_id = callback_data.question_id
    try:
        question = await question_service.delete_public_question(question_id)
    except QuestionNotFoundError:
        return await callback.answer(messages.errors.question_not_found)
    await callback.message.edit_text(
        messages.questions.delete_public_question.delete_success.format(question_text=question.text),
        reply_markup=get_to_public_questions_kb()
    )
    await state.set_state(DeletePublicQuestionStates.ID)
    await callback.answer()
    return None
