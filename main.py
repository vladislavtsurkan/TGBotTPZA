import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.mongo import MongoStorage

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config_loader import load_config_bot
from handlers import client, other, admin
from database.base import Base, get_sqlalchemy_url


async def on_startup(dp):
    print("The bot launch process has been started.")
    await other.set_default_commands(dp)
    admin.register_handlers_admin(dp)
    client.register_handlers_client(dp)
    other.register_handlers_other(dp)
    print('The bot launch process has been completed.')


async def main():

    engine = create_async_engine(
        get_sqlalchemy_url(),
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    config_bot = load_config_bot()
    bot = Bot(token=config_bot.token, parse_mode='HTML')
    bot['db'] = async_sessionmaker
    bot['ids_skip_check_registered'] = set()
    # storage = RedisStorage2('localhost', 6379, db=5, pool_size=10, prefix='my_fsm_key')
    storage = MongoStorage(host='localhost', port=27017, db_name='aiogram_fsm')
    dp = Dispatcher(bot, storage=storage)

    await on_startup(dp)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
