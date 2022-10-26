from aiogram import types, Dispatcher

from handlers.fsm.add_group import register_handlers_fsm_add_group
from services.admin import just_def


async def test(msg: types.Message):
    await just_def(msg)


def register_handlers_admin(dp: Dispatcher):
    register_handlers_fsm_add_group(dp)
    dp.register_message_handler(test, commands=['test'])
