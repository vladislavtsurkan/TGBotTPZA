from aiogram import types, Dispatcher

from handlers.fsm.add_group import register_handlers_fsm_add_group
from handlers.fsm.add_faculty import register_handlers_fsm_add_faculty
from handlers.fsm.add_department import register_handlers_fsm_add_department
from services.admin import just_def


async def test(msg: types.Message):
    await just_def(msg)


def register_handlers_admin(dp: Dispatcher):
    register_handlers_fsm_add_group(dp)
    register_handlers_fsm_add_faculty(dp)
    register_handlers_fsm_add_department(dp)
    dp.register_message_handler(test, commands=['test'])
