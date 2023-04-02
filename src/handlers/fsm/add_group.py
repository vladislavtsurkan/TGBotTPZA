from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from services.admin import (
    add_information_from_schedule_to_db,
    create_group,
    delete_group,
    is_group_exist_by_title_and_department_id
)
from services.utils import is_model_exist_by_name, is_registered_user, is_user_admin
from database.models import Department, Group

router = Router(name="fsm-add-group-router")


class FSMAddGroup(StatesGroup):
    department = State()
    title = State()
    url_schedule = State()


@router.message(Command("add_group"))
async def start_add_new_group(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    if (
            await is_registered_user(msg, session=session) and
            await is_user_admin(msg, session=session)
    ):
        await state.set_state(FSMAddGroup.department)
        await msg.answer('Введіть назву кафедри, до якої належить група.')


@router.message(FSMAddGroup.department)
async def input_department_for_add_group(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    await state.update_data(department_name=msg.text)

    is_exist, department_id = await is_model_exist_by_name(
        msg.text,
        class_model=Department,
        session=session
    )
    if is_exist:
        await msg.answer('Кафедра з такою назвою існує. Тепер введіть назву групи.')
        await state.update_data(department_id=department_id)
        await state.set_state(FSMAddGroup.title)
    else:
        await msg.answer('Помилка. Такої кафедри в базі даних не було знайдено.')


@router.message(FSMAddGroup.title)
async def input_title_for_add_group(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.update_data(title=msg.text)

    is_exist, _ = await is_group_exist_by_title_and_department_id(
        data['title'], data['department_id'], session=session
    )
    if is_exist:
        await msg.answer('Помилка. Група з такою назвою на вказаній кафедрі вже існує.')
    else:
        await msg.answer(
            'Тепер відправте посилання на розклад групи з '
            '<a href="http://epi.kpi.ua">сайту</a>.'
        )
        await state.set_state(FSMAddGroup.url_schedule)


@router.message(FSMAddGroup.url_schedule)
async def input_url_schedule_for_add_group(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.update_data(url_schedule=msg.text)

    if data.get('url_schedule', '').startswith('http://epi.kpi.ua'):
        created_group: Group = await create_group(
            data.get('department_id'),
            data.get('title'),
            data.get('url_schedule'),
            session=session
        )
        result = await add_information_from_schedule_to_db(created_group, session=session)
        if result:
            await msg.answer('Група була створена і розклад скопійовано з сайту.')
        else:
            await msg.answer('Збір даних з сайту не вдався через проблеми в його роботі.')
            await delete_group(
                group_id=created_group.id,
                department_id=created_group.department_id,
                session=session
            )
        await state.clear()
    else:
        await msg.answer('Посилання не є валідним чи направлено на сторонній сайт.')
