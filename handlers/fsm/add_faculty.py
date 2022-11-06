from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from services.admin import create_faculty
from services.utils import is_user_admin, is_model_exist_by_name
from database.models import Faculty


class FSMAddFaculty(StatesGroup):
    title = State()
    title_short = State()


async def start_add_new_faculty(msg: types.Message):
    if await is_user_admin(msg):
        await FSMAddFaculty.title.set()
        await msg.answer('Введіть назву факультету.')


async def input_faculty_title(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = msg.text

        is_exist, department_id = await is_model_exist_by_name(msg, msg.text, class_model=Faculty)
        if is_exist:
            await msg.answer('Факультет з такою назвою вже існує.')
            await state.finish()
        else:
            await msg.answer('Тепер введіть абревіатуру факультету (наприклад, ІХФ).')
            await FSMAddFaculty.next()


async def input_faculty_title_short(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title_short'] = msg.text

        if len(msg.text) > 2:
            await create_faculty(msg, data['title'], data['title_short'].upper())
            await msg.answer(f"Новий факультет було додано в базу даних: {data['title']} ({data['title_short']})")
            await state.finish()


def register_handlers_fsm_add_faculty(dp: Dispatcher):
    dp.register_message_handler(start_add_new_faculty, commands=['add_faculty'], state=None)
    dp.register_message_handler(input_faculty_title, state=FSMAddFaculty.title)
    dp.register_message_handler(input_faculty_title_short, state=FSMAddFaculty.title_short)
