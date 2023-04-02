from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from services.admin import create_department
from services.utils import is_model_exist_by_name, is_user_admin, is_registered_user
from database.models import Faculty, Department

router = Router(name="fsm-add-department-router")


class FSMAddDepartment(StatesGroup):
    faculty = State()
    title = State()
    title_short = State()


@router.message(Command("add_department"))
async def start_add_new_department(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    if (
            await is_registered_user(msg, session=session) and
            await is_user_admin(msg, session=session)
    ):
        await state.set_state(FSMAddDepartment.faculty)
        await msg.answer('Введіть назву факультету, до якого належить кафедра.')


@router.message(FSMAddDepartment.faculty)
async def input_faculty_for_add_department(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    await state.update_data(faculty_name=msg.text)

    is_exist, faculty_id = await is_model_exist_by_name(
        msg.text, class_model=Faculty, session=session
    )
    if is_exist:
        await msg.answer('Факультет з такою назвою існує. Тепер введіть назву кафедри.')
        await state.update_data(faculty_id=faculty_id)
        await state.set_state(FSMAddDepartment.title)
    else:
        await msg.answer('Помилка. Такого факультету в базі даних не було знайдено.')


@router.message(FSMAddDepartment.title)
async def input_title_for_add_department(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    await state.update_data(title=msg.text)

    is_exist, department_id = await is_model_exist_by_name(
        msg.text, class_model=Department, session=session
    )
    if is_exist:
        await msg.answer('Помилка. Кафедра з такою назвою вже існує.')
    else:
        await msg.answer('Тепер введіть абревіатуру кафедри (наприклад, ТПЗА).')
        await state.set_state(FSMAddDepartment.title_short)


@router.message(FSMAddDepartment.title_short)
async def input_title_short_for_add_department(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    await state.update_data(title_short=msg.text)

    if len(msg.text) >= 2:
        data = await state.get_data()
        await create_department(
           data['faculty_id'], data['title'], data['title_short'].upper(), session=session
        )
        await msg.answer(
            f"Нову кафедру було додано в базу даних: {data['title']} ({data['title_short']})."
        )
        await state.clear()
