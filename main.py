import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatType
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from redis.asyncio import Redis

from bot.config import env_config
from bot.database import init_db
from bot.handlers import *
from bot.middlewares import UserMiddleware, ServicesMiddleware
from bot.services import FightManager


async def start_main_bot():
    bot = Bot(token=env_config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    storage = RedisStorage(redis=Redis(host=env_config.REDIS_HOST, port=env_config.REDIS_PORT),
                           key_builder=DefaultKeyBuilder(with_destiny=True, with_bot_id=True))
    dp = Dispatcher(storage=storage)

    dp.message.filter(F.chat.type == ChatType.PRIVATE)

    fight_manager = FightManager()

    dp.update.outer_middleware(UserMiddleware())
    dp.message.middleware.register(ServicesMiddleware(fight_manager))
    dp.callback_query.middleware.register(ServicesMiddleware(fight_manager))

    dp.include_router(user_main_router)
    dp.include_router(questions_router)
    dp.include_router(test_router)
    dp.include_router(user_settings_router)
    dp.include_router(adminka_router)
    dp.include_router(fight_router)

    commands = [
        BotCommand(command="main", description="В главное меню"),
    ]
    await bot.set_my_commands(commands)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    await init_db()
    await start_main_bot()

if __name__ == "__main__":
    asyncio.run(main())
