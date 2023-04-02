from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Text, Command

from sqlalchemy.ext.asyncio import AsyncSession

from services.admin import (
    get_department_instance_by_title,
    change_faculty_for_department,
    delete_department,
    change_title_for_department
)
from services.utils import is_model_exist_by_name, is_registered_user, is_user_admin
from keyboards.kb_edit_department import get_keyboard_edit_department
from database.models import Department, Faculty

router = Router(name="fsm-edit-department-router")


class FSMEditDepartment(StatesGroup):
    title = State()
    select_edit_department = State()
    input_edit_title = State()
    input_edit_title_short = State()
    input_edit_faculty = State()


@router.message(Command("edit_department"))
async def start_edit_department(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    if (
            await is_registered_user(msg, session=session) and
            await is_user_admin(msg, session=session)
    ):
        await state.set_state(FSMEditDepartment.title)
        await msg.answer('Введіть назву кафедри.')


@router.message(FSMEditDepartment.title)
async def input_title_for_edit_department(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    await state.update_data(title=msg.text)

    department_instance: Department = await get_department_instance_by_title(
        msg.text,
        session=session
    )
    if department_instance:
        await msg.answer(
            f'<b>Інформація про кафедру</b>\n'
            f'Факультет: {department_instance.Faculty.title} ({department_instance.Faculty.title_short})\n'
            f'Кафедра: {department_instance.title} ({department_instance.title_short})',
            reply_markup=get_keyboard_edit_department()
        )
        await state.update_data(department_id=department_instance.id)
        await state.set_state(FSMEditDepartment.select_edit_department)
    else:
        await msg.answer('Помилка. Такої кафедри в базі даних не було знайдено.')


@router.callback_query(FSMEditDepartment.select_edit_department)
@router.callback_query(F.data.startswith('group'))
async def department_edit_callback(
        callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    data_inline_keyboard = callback.data.split()

    match data_inline_keyboard:
        case 'department', 'change_title':
            await callback.message.edit_text(
                'Введіть нову назву для кафедри.', reply_markup=None
            )
            await state.set_state(FSMEditDepartment.input_edit_title)
        case 'department', 'change_faculty':
            await callback.message.edit_text(
                'Введіть назву нового факультету для кафедри.', reply_markup=None
            )
            await state.set_state(FSMEditDepartment.input_edit_faculty)
        case 'department', 'delete_department':
            await callback.message.edit_text(
                'Кафедру разом зі зв\'язаними групами було видалено!',
                reply_markup=None
            )
            data = await state.get_data()
            await delete_department(department_id=data['department_id'], session=session)
            await state.clear()

    await callback.answer()


@router.message(FSMEditDepartment.input_edit_title)
async def input_new_title_for_edit_department(msg: types.Message, state: FSMContext) -> None:
    await state.update_data(new_title=msg.text)
    await msg.answer(f'Тепер введіть нову абревіатуру для кафедри.')
    await state.set_state(FSMEditDepartment.input_edit_title_short)


@router.message(FSMEditDepartment.input_edit_title_short)
async def input_new_title_short_for_edit_department(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.update_data(new_title_short=msg.text)
    await msg.answer(
        f'Назва кафедри була змінена на: {data["new_title"]} ({data["new_title_short"]})'
    )
    await change_title_for_department(
        department_id=data['department_id'],
        title=data['new_title'],
        title_short=data['new_title_short'],
        session=session
    )
    await state.clear()


@router.message(FSMEditDepartment.input_edit_faculty)
async def input_new_faculty_for_edit_department(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    await state.update_data(department_name=msg.text)

    is_exist, faculty_id = await is_model_exist_by_name(
        msg.text, class_model=Faculty, session=session
    )
    if is_exist:
        data = await state.update_data(new_faculty_id=faculty_id)
        await change_faculty_for_department(
            department_id=data['department_id'],
            faculty_id=data['new_faculty_id'],
            session=session
        )
        await msg.answer('Факультет було успішно замінено!')
        await state.clear()
    else:
        await msg.answer('Помилка. Такого факультету в базі даних не було знайдено.')
