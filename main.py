import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from redis.asyncio import Redis

from bot.database import init_db
from bot.handlers import *
from bot.middlewares import UserMiddleware


async def start_main_bot():
    bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode="HTML"))
    storage = RedisStorage(Redis(), key_builder=DefaultKeyBuilder(with_destiny=True, with_bot_id=True))
    dp = Dispatcher(storage=storage)

    dp.update.outer_middleware(UserMiddleware())

    dp.include_router(user_main_router)
    dp.include_router(create_question_router)
    dp.include_router(test_router)
    dp.include_router(user_settings_router)

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
    init_db()
    await start_main_bot()

if __name__ == "__main__":
    asyncio.run(main())
