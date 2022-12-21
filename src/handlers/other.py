from loguru import logger

from aiogram import types, Dispatcher
from aiogram.utils.exceptions import BotBlocked

from handlers.fsm.decorators import check_user_is_registered


async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    """Error handling (BotBlocked)"""
    print(f"Мене заблокував користувач!\nПовідомлення: {update}\nПомилка: {exception}")
    return True


async def set_default_commands(dp: Dispatcher):
    logger.debug("Start set default commands for bot")
    await dp.bot.set_my_commands([
        types.BotCommand("help", "Інформація"),
        types.BotCommand("today", "Пари на сьогодні"),
        types.BotCommand("tomorrow", "Пари завтра"),
        types.BotCommand("current_week", "Пари поточного тижня"),
        types.BotCommand("next_week", "Пари наступного тижня"),
        types.BotCommand("cancel", "Відміна дії"),
    ])
    logger.debug("Success set default commands for bot")


@check_user_is_registered
async def get_text_messages(msg: types.Message):
    print(f'{msg}')
    match msg.text.lower():
        case 'сайт' | 'site':
            await msg.answer('<a href="http://epi.kpi.ua">Розклад КПІ</a>')
        case 'google' | 'гугл':
            await msg.answer('<a href="https://google.com">Посилання</a>')
        case 'розробник' | 'developer':
            await msg.answer('<b>Мій аккаунт: </b><a href="t.me/vladyslavtsurkan">Telegram</a>')
        case _:
            await msg.answer('Я вас не розумію.')


def register_handlers_other(dp: Dispatcher):
    logger.debug('Start registration handlers for "other"')
    dp.register_errors_handler(error_bot_blocked, exception=BotBlocked)
    dp.register_message_handler(get_text_messages, content_types=['text'])
    logger.debug('Stop registration handlers for "other"')
