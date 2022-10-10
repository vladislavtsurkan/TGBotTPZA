from aiogram.utils import executor
from create_bot import dp
from handlers import client, other
from database.mysql_database import update_database


async def on_startup(_):
    update_database()

    print("The bot launch process has been started.")
    await other.set_default_commands(dp)
    client.register_handlers_client(dp)
    other.register_handlers_other(dp)
    print('The bot launch process has been completed.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
