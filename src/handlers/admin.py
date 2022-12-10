from loguru import logger
from aiogram import types, Dispatcher

from src.handlers.fsm.decorators import check_user_is_admin, check_user_is_registered

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


@check_user_is_registered
@check_user_is_admin
async def get_admin_commands(msg: types.Message):
    await msg.answer(_admin_commands)


def register_handlers_admin(dp: Dispatcher):
    logger.debug('Start registration handlers for admin')
    dp.register_message_handler(get_admin_commands, commands=['cmds'])
    logger.debug('Stop registration handlers for admin')
