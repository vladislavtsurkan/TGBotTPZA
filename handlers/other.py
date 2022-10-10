from aiogram import types, Dispatcher
from aiogram.utils.exceptions import BotBlocked


async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    """Error handling (BotBlocked)"""
    print(f"Мене заблокував користувач!\nПовідомлення: {update}\nПомилка: {exception}")
    return True


async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand("help", "Інформація"),
    ])


async def get_text_messages(msg: types.Message):
    await msg.answer('Я вас не розумію.')


def register_handlers_other(dp: Dispatcher):
    dp.register_errors_handler(error_bot_blocked, exception=BotBlocked)
    dp.register_message_handler(get_text_messages, content_types=['text'])
