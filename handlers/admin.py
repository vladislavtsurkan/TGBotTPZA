from loguru import logger
from aiogram import types, Dispatcher

from services.admin import just_def


async def test(msg: types.Message):
    await just_def(msg)


def register_handlers_admin(dp: Dispatcher):
    logger.debug('Start registration handlers for admin')
    dp.register_message_handler(test, commands=['test'])
    logger.debug('Stop registration handlers for admin')
