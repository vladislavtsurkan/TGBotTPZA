from aiogram.dispatcher.filters import Text
from loguru import logger
from aiogram import types, Dispatcher

from handlers.fsm.decorators import check_user_is_registered
from services.utils import get_current_week_number
from services.client import (
    get_lessons_today_or_tomorrow_for_user,
    get_lessons_current_or_next_week_for_user,
    get_group_id_by_user_id
)
from services.admin import get_groups_instances_by_title
from keyboards.kb_with_groups_schedule import get_keyboard_with_groups



@check_user_is_registered(allow_function=True)
async def send_welcome(msg: types.Message):
    await msg.answer(
        f'Я бот-помічник для пошуку розкладу в КПІ. Приємно познайомитись, '
        f'{msg.from_user.first_name}.\n'
        f'Для початку роботи зі мною Ви повинні вказати групу, розклад якої вас цікавить.'
    )


@check_user_is_registered
async def get_current_week_lessons(msg: types.Message):
    group_id = await get_group_id_or_none(msg)
    if group_id is None:
        return

    answer = await get_lessons_current_or_next_week_for_user(
        msg.bot.get('db'),
        group_id=group_id,
        week=get_current_week_number()
    )
    await msg.answer(answer)


@check_user_is_registered
async def get_next_week_lessons(msg: types.Message):
    group_id = await get_group_id_or_none(msg)
    if group_id is None:
        return

    answer = await get_lessons_current_or_next_week_for_user(
        msg.bot.get('db'),
        group_id=group_id,
        week=get_current_week_number(),
        next_week=True
    )
    await msg.answer(answer)


@check_user_is_registered
async def get_today_lessons(msg: types.Message):
    group_id = await get_group_id_or_none(msg)
    if group_id is None:
        return

    answer = await get_lessons_today_or_tomorrow_for_user(
        msg.bot.get('db'),
        group_id=group_id,
        week=get_current_week_number()
    )
    await msg.answer(answer)


@check_user_is_registered
async def get_tomorrow_lessons(msg: types.Message):
    group_id = await get_group_id_or_none(msg)
    if group_id is None:
        return

    answer = await get_lessons_today_or_tomorrow_for_user(
        msg.bot.get('db'),
        group_id=group_id,
        week=get_current_week_number(),
        tomorrow=True
    )
    await msg.answer(answer)


async def get_group_id_or_none(msg: types.Message) -> int | None:
    """
    Check exist input group title. If not, send message. If yes, return group id.
    If in database exist more than one group with same title, send message with list of groups.
    """
    data = msg.text.split() # /today <group_title>
    if len(data) == 1:
        return await get_group_id_by_user_id(msg.bot.get('db'), user_id=msg.from_user.id)
    else:
        groups = await get_groups_instances_by_title(msg.bot.get('db'), data[1])
        match len(groups):
            case 0:
                await msg.answer(f'Група з назвою <b>{data[1]}</b> не знайдена в базі даних.')
                return
            case 1:
                return groups[0].id
            case _:
                await msg.answer(
                    f'Знайдено декілька груп з назвою <b>{data[1]}</b>. Оберіть потрібну:',
                    reply_markup=get_keyboard_with_groups(groups, data[0][1:])
                )
                return


async def group_schedule_callback(callback: types.CallbackQuery):
    data_inline_keyboard = callback.data.split()
    group_id = int(data_inline_keyboard[3])

    match data_inline_keyboard[2]:
        case 'today':
            answer = await get_lessons_today_or_tomorrow_for_user(
                callback.bot.get('db'),
                group_id=group_id,
                week=get_current_week_number()
            )
        case 'tomorrow':
            answer = await get_lessons_today_or_tomorrow_for_user(
                callback.bot.get('db'),
                group_id=group_id,
                week=get_current_week_number(),
                tomorrow=True
            )
        case 'current_week':
            answer = await get_lessons_current_or_next_week_for_user(
                callback.bot.get('db'),
                group_id=group_id,
                week=get_current_week_number()
            )
        case 'next_week':
            answer = await get_lessons_current_or_next_week_for_user(
                callback.bot.get('db'),
                group_id=group_id,
                week=get_current_week_number(),
                next_week=True
            )
        case _:
            logger.error(f'Unknown command: {data_inline_keyboard[2]}')
            return

    await callback.message.edit_text(answer, reply_markup=None)
    await callback.answer()


def register_handlers_client(dp: Dispatcher):
    logger.debug('Start registration handlers for client (User)')
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
    dp.register_message_handler(get_today_lessons, commands=['today'])
    dp.register_message_handler(get_tomorrow_lessons, commands=['tomorrow'])
    dp.register_message_handler(get_current_week_lessons, commands=['current_week'])
    dp.register_message_handler(get_next_week_lessons, commands=['next_week'])
    dp.register_callback_query_handler(
        group_schedule_callback, Text(startswith='group schedule')
    )
    logger.debug('Stop registration handlers for client (User)')
