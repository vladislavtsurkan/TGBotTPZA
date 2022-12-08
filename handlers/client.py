from loguru import logger
from aiogram import types, Dispatcher

from services.utils import (
    is_registered_user,
    get_current_week_number,
    check_if_user_is_registered
)
from services.client import (
    get_lessons_today_or_tomorrow_for_user,
    get_lessons_current_or_next_week_for_user
)
from handlers.fsm.registration import FSMRegistration


async def send_welcome(msg: types.Message):
    await msg.answer(
        f'Я бот-помічник для пошуку розкладу в КПІ. Приємно познайомитись, '
        f'{msg.from_user.first_name}.\n'
        f'Поки що я нічого не вмію, але це ненадовго =]'
    )

    if not await is_registered_user(msg):
        await msg.answer('Будь ласка, введіть назву Вашої групи.')
        await FSMRegistration.group.set()


@check_if_user_is_registered
async def get_current_week_lessons(msg: types.Message):
    answer = await get_lessons_current_or_next_week_for_user(
        msg.bot.get('db'),
        user_id=msg.from_user.id,
        week=get_current_week_number()
    )
    await msg.answer(answer)


@check_if_user_is_registered
async def get_next_week_lessons(msg: types.Message):
    answer = await get_lessons_current_or_next_week_for_user(
        msg.bot.get('db'),
        user_id=msg.from_user.id,
        week=get_current_week_number(),
        next_week=True
    )
    await msg.answer(answer)


@check_if_user_is_registered
async def get_today_lessons(msg: types.Message):
    answer = await get_lessons_today_or_tomorrow_for_user(
        msg.bot.get('db'),
        user_id=msg.from_user.id,
        week=get_current_week_number()
    )
    await msg.answer(answer)


@check_if_user_is_registered
async def get_tomorrow_lessons(msg: types.Message):
    answer = await get_lessons_today_or_tomorrow_for_user(
        msg.bot.get('db'),
        user_id=msg.from_user.id,
        week=get_current_week_number(),
        tomorrow=True
    )
    await msg.answer(answer)


def register_handlers_client(dp: Dispatcher):
    logger.debug('Start registration handlers for client (User)')
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
    dp.register_message_handler(get_today_lessons, commands=['today'])
    dp.register_message_handler(get_tomorrow_lessons, commands=['tomorrow'])
    dp.register_message_handler(get_current_week_lessons, commands=['current_week'])
    dp.register_message_handler(get_next_week_lessons, commands=['next_week'])
    logger.debug('Stop registration handlers for client (User)')
