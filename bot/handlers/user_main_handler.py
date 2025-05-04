from aiogram import Router, F, Bot
from aiogram.filters import or_f, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import messages
from bot.enums import UserRole
from bot.filters import RoleFilter
from bot.keyboards import get_main_kb
from bot.services import FightManager

router = Router(name="user_main_router")

router.message.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))
router.callback_query.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))


@router.message(
    Command(commands=["start", "main", "cancel"]),
    flags={"services": ["fight"]},
)
@router.callback_query(
    F.data.in_({"main", "cancel"}),
    flags={"services": ["fight"]},
)
async def main(event: Message | CallbackQuery, state: FSMContext, fight_manager: FightManager, bot: Bot):
    fight_session = fight_manager.get_session_by_player(event.from_user.id)
    if fight_session is not None:
        await fight_session.leave_player(event.from_user.id, bot)
    else:
        fight_manager.leave_waiting_player(event.from_user.id)
    message: Message = event.message if isinstance(event, CallbackQuery) else event
    await message.answer(
        text=messages.main_menu,
        reply_markup=get_main_kb(),
    )
    await state.clear()
    if isinstance(event, CallbackQuery):
        await event.answer()
