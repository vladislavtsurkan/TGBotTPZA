from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from services.admin import (
    get_faculty_instance_by_title,
    change_title_for_faculty,
    delete_faculty
)
from keyboards.kb_edit_faculty import get_keyboard_edit_faculty
from database.models import Faculty
from services.utils import is_registered_user, is_user_admin

router = Router(name="fsm-edit-faculty-router")


class FSMEditFaculty(StatesGroup):
    title = State()
    select_edit_faculty = State()
    input_edit_title = State()
    input_edit_title_short = State()


@router.message(Command("edit_faculty"))
async def start_edit_faculty(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    if (
            await is_registered_user(msg, session=session) and
            await is_user_admin(msg, session=session)
    ):
        await state.set_state(FSMEditFaculty.title)
        await msg.answer('Введіть назву факультета.')


@router.message(FSMEditFaculty.title)
async def input_title_for_edit_faculty(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    await state.update_data(title=msg.text)

    faculty_instance: Faculty = await get_faculty_instance_by_title(msg.text, session=session)
    if faculty_instance:
        await msg.answer(
            f'<b>Інформація про факультет</b>\n'
            f'Факультет: {faculty_instance.title} ({faculty_instance.title_short})',
            reply_markup=get_keyboard_edit_faculty()
        )
        await state.update_data(faculty_id=faculty_instance.id)
        await state.set_state(FSMEditFaculty.select_edit_faculty)
    else:
        await msg.answer('Помилка. Такого факультету в базі даних не було знайдено.')


@router.callback_query(FSMEditFaculty.select_edit_faculty)
@router.callback_query(F.data.startswith('group'))
async def faculty_edit_callback(
        callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    data_inline_keyboard = callback.data.split()

    match data_inline_keyboard:
        case 'faculty', 'change_title':
            await callback.message.edit_text(
                'Введіть нову назву для факультета.', reply_markup=None
            )
            await state.set_state(FSMEditFaculty.input_edit_title)
        case 'faculty', 'delete_faculty':
            await callback.message.edit_text(
                'Факультет разом зі зв\'язаними кафедрами та групами було видалено!',
                reply_markup=None
            )
            data = await state.get_data()
            await delete_faculty(faculty_id=data['faculty_id'], session=session)
            await state.clear()

    await callback.answer()


@router.message(FSMEditFaculty.input_edit_title)
async def input_new_title_for_edit_faculty(msg: types.Message, state: FSMContext) -> None:
    await state.update_data(new_title=msg.text)
    await msg.answer(f'Тепер введіть нову абревіатуру для факультета.')
    await state.set_state(FSMEditFaculty.input_edit_title_short)


@router.message(FSMEditFaculty.input_edit_title_short)
async def input_new_title_short_for_edit_faculty(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.update_data(new_title_short=msg.text)
    await msg.answer(
        f'Назва факультету була змінена на: {data["new_title"]} ({data["new_title_short"]})'
    )
    await change_title_for_faculty(
        faculty_id=data['faculty_id'],
        title=data['new_title'],
        title_short=data['new_title_short'],
        session=session
    )
    await state.clear()
