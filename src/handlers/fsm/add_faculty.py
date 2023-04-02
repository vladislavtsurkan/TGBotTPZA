from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from services.admin import create_faculty
from services.utils import is_model_exist_by_name, is_registered_user, is_user_admin
from database.models import Faculty

router = Router(name="fsm-add-faculty-router")


class FSMAddFaculty(StatesGroup):
    title = State()
    title_short = State()


@router.message(Command("add_faculty"))
async def start_add_new_faculty(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    if (
            await is_registered_user(msg, session=session) and
            await is_user_admin(msg, session=session)
    ):
        await state.set_state(FSMAddFaculty.title)
        await msg.answer('Введіть назву факультету.')


@router.message(FSMAddFaculty.title)
async def input_faculty_title(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    await state.update_data(title=msg.text)

    is_exist, _ = await is_model_exist_by_name(msg.text, class_model=Faculty, session=session)
    if is_exist:
        await msg.answer('Факультет з такою назвою вже існує.')
        await state.clear()
    else:
        await msg.answer('Тепер введіть абревіатуру факультету (наприклад, ІХФ).')
        await state.set_state(FSMAddFaculty.title_short)


@router.message(FSMAddFaculty.title_short)
async def input_faculty_title_short(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    await state.update_data(title_short=msg.text)

    if len(msg.text) >= 2:
        data = await state.get_data()
        await create_faculty(data['title'], data['title_short'].upper(), session=session)
        await msg.answer(
            f"Новий факультет було додано в базу даних: {data['title']} "
            f"({data['title_short']})."
        )
        await state.clear()
