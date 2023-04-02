from aiogram.fsm.context import FSMContext
from loguru import logger

from aiogram import types, Bot, Router
from aiogram.filters import Text
from sqlalchemy.ext.asyncio import AsyncSession

from handlers.fsm.registration import start_registration
from services.utils import is_registered_user

router = Router(name="other-commands")


async def set_default_commands(bot: Bot):
    logger.debug("Start set default commands for bot")
    await bot.set_my_commands([
        types.BotCommand(command="help", description="Інформація"),
        types.BotCommand(command="today", description="Пари на сьогодні"),
        types.BotCommand(command="tomorrow", description="Пари завтра"),
        types.BotCommand(command="current_week", description="Пари поточного тижня"),
        types.BotCommand(command="next_week", description="Пари наступного тижня"),
        types.BotCommand(command="cancel", description="Відміна дії"),
    ])
    logger.debug("Success set default commands for bot")


@router.message(Text)
async def get_text_messages(
        msg: types.Message, session: AsyncSession, state: FSMContext
) -> None:
    if not await is_registered_user(msg, session=session):
        await start_registration(msg, state)
        return

    match msg.text.lower():
        case 'сайт' | 'site':
            await msg.answer('<a href="http://epi.kpi.ua">Розклад КПІ</a>')
        case 'google' | 'гугл':
            await msg.answer('<a href="https://google.com">Посилання</a>')
        case 'розробник' | 'developer':
            await msg.answer('<b>Мій аккаунт: </b><a href="t.me/vladyslavtsurkan">Telegram</a>')
        case _:
            await msg.answer('Я вас не розумію.')
