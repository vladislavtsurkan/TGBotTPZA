from loguru import logger
from aiogram import types, Dispatcher

from services.utils import is_user_admin

_admin_commands = """
<b>👨‍💻 Команди адміністратора:</b>

/cmds - список команд
/add_faculty - додати факультет
/edit_faculty - редагувати факультет
/add_department - додати кафедру
/edit_department - редагувати кафедру
/add_group - додати групу
/edit_group - редагувати групу
"""


async def get_admin_commands(msg: types.Message):
    if await is_user_admin(msg):
        await msg.answer(_admin_commands)


def register_handlers_admin(dp: Dispatcher):
    logger.debug('Start registration handlers for admin')
    dp.register_message_handler(get_admin_commands, commands=['cmds'])
    logger.debug('Stop registration handlers for admin')
