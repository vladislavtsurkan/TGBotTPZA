import asyncio
from pathlib import Path
from loguru import logger
from redis.asyncio.client import Redis

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from config_loader import load_config_bot, BotConfig, load_config_redis, RedisConfig
from handlers import client, other, admin
from handlers.fsm import router as router_fsm
from database.base import sessionmaker_async
from middlewares import DbSessionMiddleware

logs_folder = Path("logs")
if not logs_folder.exists():
    Path.mkdir(logs_folder)

logger.add('logs/bot.log', rotation='10 MB', compression='zip', enqueue=True, level="WARNING")


async def main():
    config_bot: BotConfig = load_config_bot()
    bot = Bot(token=config_bot.token, parse_mode='HTML')

    config_redis: RedisConfig = load_config_redis()
    storage = RedisStorage(
        Redis(
            host=config_redis.host,
            password=config_redis.password,
            db=config_redis.db,
            port=config_redis.port,
        )
    )
    dp = Dispatcher(storage=storage)
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker_async))

    # including routers
    dp.include_router(router_fsm)
    dp.include_router(admin.router)
    dp.include_router(client.router)
    dp.include_router(other.router)

    await other.set_default_commands(bot)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()
        await logger.complete()


if __name__ == '__main__':
    asyncio.run(main())
