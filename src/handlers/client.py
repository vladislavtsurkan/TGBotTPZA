from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger
from aiogram import types, Router, F

from sqlalchemy.ext.asyncio import AsyncSession

from handlers.fsm.registration import start_registration
from services.client import (
    get_lessons_today_or_tomorrow_for_user,
    get_lessons_current_or_next_week_for_user,
    get_group_id_by_user_id
)
from services.admin import get_groups_instances_by_title
from keyboards.kb_with_groups_schedule import get_keyboard_with_groups
from services.utils import is_registered_user

router = Router(name="client-commands")


@router.message(Command(commands=["help", "start"]))
async def send_welcome(
        msg: types.Message, session: AsyncSession, state: FSMContext
) -> None:
    await msg.answer(
        f'Я бот-помічник для пошуку розкладу в КПІ. Приємно познайомитись, '
        f'{msg.from_user.first_name}.\n'
        f'Для початку роботи зі мною Ви повинні вказати групу, розклад якої вас цікавить.'
    )

    if not await is_registered_user(msg, session=session):
        await start_registration(msg, state)


@router.message(Command("current_week"))
async def get_current_week_lessons(
        msg: types.Message, session: AsyncSession, state: FSMContext
) -> None:
    if not await is_registered_user(msg, session=session):
        await start_registration(msg, state)
        return

    group_id = await get_group_id_or_none(msg, session=session)
    if group_id is None:
        return

    answer = await get_lessons_current_or_next_week_for_user(
        group_id=group_id,
        session=session
    )
    await msg.answer(answer)


@router.message(Command("next_week"))
async def get_next_week_lessons(
        msg: types.Message, session: AsyncSession, state: FSMContext
) -> None:
    if not await is_registered_user(msg, session=session):
        await start_registration(msg, state)
        return

    group_id = await get_group_id_or_none(msg, session=session)
    if group_id is None:
        return

    answer = await get_lessons_current_or_next_week_for_user(
        group_id=group_id,
        next_week=True,
        session=session
    )
    await msg.answer(answer)


@router.message(Command("today"))
async def get_today_lessons(
        msg: types.Message, session: AsyncSession, state: FSMContext
) -> None:
    if not await is_registered_user(msg, session=session):
        await start_registration(msg, state)
        return

    group_id = await get_group_id_or_none(msg, session=session)
    if group_id is None:
        return

    answer = await get_lessons_today_or_tomorrow_for_user(
        group_id=group_id,
        session=session
    )
    await msg.answer(answer)


@router.message(Command("tomorrow"))
async def get_tomorrow_lessons(
        msg: types.Message, session: AsyncSession, state: FSMContext
) -> None:
    if not await is_registered_user(msg, session=session):
        await start_registration(msg, state)
        return

    group_id = await get_group_id_or_none(msg, session=session)
    if group_id is None:
        return

    answer = await get_lessons_today_or_tomorrow_for_user(
        group_id=group_id,
        tomorrow=True,
        session=session
    )
    await msg.answer(answer)


async def get_group_id_or_none(msg: types.Message, session: AsyncSession) -> int | None:
    """
    Check exist input group title. If not, send message. If yes, return group id.
    If in database exist more than one group with same title, send message with list of groups.
    """
    data = msg.text.split()  # /today <group_title>
    if len(data) == 1:
        return await get_group_id_by_user_id(user_id=msg.from_user.id, session=session)
    else:
        groups = await get_groups_instances_by_title(data[1], session=session)
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


@router.callback_query(F.data.startswith('group schedule'))
async def group_schedule_callback(callback: types.CallbackQuery, session: AsyncSession) -> None:
    data_inline_keyboard = callback.data.split()
    group_id = int(data_inline_keyboard[3])

    match data_inline_keyboard[2]:
        case 'today':
            answer = await get_lessons_today_or_tomorrow_for_user(
                group_id=group_id,
                session=session
            )
        case 'tomorrow':
            answer = await get_lessons_today_or_tomorrow_for_user(
                group_id=group_id,
                tomorrow=True,
                session=session
            )
        case 'current_week':
            answer = await get_lessons_current_or_next_week_for_user(
                group_id=group_id,
                session=session
            )
        case 'next_week':
            answer = await get_lessons_current_or_next_week_for_user(
                group_id=group_id,
                next_week=True,
                session=session
            )
        case _:
            logger.error(f'Unknown command: {data_inline_keyboard[2]}')
            return

    await callback.message.edit_text(answer, reply_markup=None)
    await callback.answer()
