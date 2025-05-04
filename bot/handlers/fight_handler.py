from aiogram import Router, F, Bot
from aiogram.filters import or_f, Command
from aiogram.types import Message, CallbackQuery

from bot.config import messages, config
from bot.enums import UserRole
from bot.filters import RoleFilter
from bot.models import User
from bot.services import FightManager, QuestionService
from bot.services.exceptions import DateParsingError

router = Router(name="fight_router")

router.message.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))
router.callback_query.filter(or_f(RoleFilter(UserRole.USER), RoleFilter(UserRole.ADMIN)))


@router.callback_query(
    F.data == "fight",
    flags={"services": ["fight"]},
)
@router.message(
    Command("fight"),
    flags={"services": ["fight"]},
)
async def fight_button_handler(event: Message | CallbackQuery, bot: Bot, user: User, fight_manager: FightManager):
    message: Message = event.message if isinstance(event, CallbackQuery) else event
    session = await fight_manager.add_waiting_player(user, bot)
    if session is not None:
        await session.start_game(bot)
    else:
        await message.answer(messages.fight.wait_join.format(time=config.fight_waiting_player_timeout))
    if isinstance(event, CallbackQuery):
        await event.answer()


@router.message(
    F.text.as_("answer_text"),
    flags={"services": ["fight"]},
)
async def game_message_handler(message: Message, bot: Bot, answer_text: str, fight_manager: FightManager):
    user_id = message.from_user.id
    session = fight_manager.get_session_by_player(user_id)
    if session is None:
        return None
    try:
        answer = QuestionService.parse_date_string(answer_text)
    except DateParsingError:
        return await message.answer(messages.errors.date_parsing_error)
    await session.process_answer(user_id, answer, bot)
    await message.delete()
    return None
