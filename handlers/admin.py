from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from services.admin import just_def, delete_group


async def test(msg: types.Message):
    await just_def(msg)


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(test, commands=['test'])
    # dp.register_callback_query_handler(group_edit_callback, Text(startswith='group'))
