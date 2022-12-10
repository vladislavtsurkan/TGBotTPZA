from loguru import logger

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from src.handlers.fsm.add_group import register_handlers_fsm_add_group
from src.handlers.fsm.add_faculty import register_handlers_fsm_add_faculty
from src.handlers.fsm.add_department import register_handlers_fsm_add_department
from src.handlers.fsm.edit_group import register_handlers_fsm_edit_group
from src.handlers.fsm.edit_department import register_handlers_fsm_edit_department
from src.handlers.fsm.edit_faculty import register_handlers_fsm_edit_faculty
from src.handlers.fsm.registration import register_handlers_fsm_registration


async def cancel_handler(msg: types.Message, state: FSMContext):
    if await state.get_state() is None:
        return
    await state.finish()
    await msg.answer('Дію було відмінено.')


def register_all_fsm_handlers(dp: Dispatcher):
    logger.debug('Start registration handlers for FSMs')
    dp.register_message_handler(
        cancel_handler, state='*',
        commands=[
            'відміна', 'stop', 'cancel'
        ]
    )
    dp.register_message_handler(cancel_handler, Text(
        equals=[
            'відміна', 'cancel', 'stop', 'стоп', '-', 'отмена', 'выйти', 'вийти'
        ],
        ignore_case=True
    ), state='*')

    # admin
    register_handlers_fsm_add_group(dp)
    register_handlers_fsm_add_faculty(dp)
    register_handlers_fsm_add_department(dp)
    register_handlers_fsm_edit_group(dp)
    register_handlers_fsm_edit_department(dp)
    register_handlers_fsm_edit_faculty(dp)

    # other
    register_handlers_fsm_registration(dp)
    logger.debug('Stop registration handlers for FSMs')
