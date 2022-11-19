from loguru import logger
from aiogram import types, Dispatcher

from services.utils import is_registered_user
from handlers.fsm.registration import FSMRegistration


async def send_welcome(msg: types.Message):
    await msg.answer(f'Я бот-помічник для пошуку розкладу в КПІ. Приємно познайомитись, '
                     f'{msg.from_user.first_name}.\n'
                     f'Поки що я нічого не вмію, але це ненадовго =]')

    if not await is_registered_user(msg):
        await msg.answer('Ви ще не зареєстровані. Будь ласка, введіть назву Вашої групи.')
        await FSMRegistration.group.set()


def register_handlers_client(dp: Dispatcher):
    logger.debug('Start registration handlers for client (User)')
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
    logger.debug('Stop registration handlers for client (User)')
