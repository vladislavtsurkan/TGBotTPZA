from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from services.admin import create_department
from services.utils import is_user_admin, is_model_exist_by_name
from database.models import Faculty, Department


class FSMAddDepartment(StatesGroup):
    faculty = State()
    title = State()
    title_short = State()


async def start_add_new_department(msg: types.Message):
    if await is_user_admin(msg):
        await FSMAddDepartment.faculty.set()
        await msg.answer('Введіть назву факультету, до якого належить кафедра.')


async def input_faculty_for_add_department(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['faculty_name'] = msg.text

        is_exist, faculty_id = await is_model_exist_by_name(msg.bot.get('db'), msg.text, class_model=Faculty)
        if is_exist:
            await msg.answer('Факультет з такою назвою існує. Тепер введіть назву кафедри.')
            data['faculty_id'] = faculty_id
            await FSMAddDepartment.next()
        else:
            await msg.answer('Помилка. Такого факультету в базі даних не було знайдено.')


async def input_title_for_add_department(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = msg.text

        is_exist, department_id = await is_model_exist_by_name(msg.bot.get('db'), msg.text, class_model=Department)
        if is_exist:
            await msg.answer('Помилка. Кафедра з такою назвою вже існує.')
        else:
            await msg.answer('Тепер введіть абревіатуру кафедри (наприклад, ТПЗА).')
            await FSMAddDepartment.next()


async def input_title_short_for_add_department(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title_short'] = msg.text

        if len(msg.text) > 2:
            await create_department(msg.bot.get('db'), data['faculty_id'], data['title'], data['title_short'].upper())
            await msg.answer(f"Нову кафедру було додано в базу даних: {data['title']} ({data['title_short']})")
            await state.finish()


def register_handlers_fsm_add_department(dp: Dispatcher):
    dp.register_message_handler(start_add_new_department, commands=['add_department'], state=None)
    dp.register_message_handler(input_faculty_for_add_department, state=FSMAddDepartment.faculty)
    dp.register_message_handler(input_title_for_add_department, state=FSMAddDepartment.title)
    dp.register_message_handler(input_title_short_for_add_department, state=FSMAddDepartment.title_short)
