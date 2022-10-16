from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from services.other import is_model_exist_by_name
from services.admin import is_user_admin, add_information_from_schedule_to_db
from database.models import Faculty, Department, Group, User


class FSMAddGroup(StatesGroup):
    department = State()
    title = State()
    url_schedule = State()


async def start_add_new_group(msg: types.Message):
    if await is_user_admin(msg):
        await FSMAddGroup.department.set()
        await msg.answer('Введіть назву кафедри, до якої належить група')


async def input_department_for_add_group(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'відміна':
        await state.finish()
        return

    async with state.proxy() as data:
        data['department_name'] = msg.text

        is_exist, department_id = await is_model_exist_by_name(msg, msg.text, class_model=Department)
        if is_exist:
            await msg.answer('Кафедра з такою назвою існує. Тепер введіть назву групи.')
            data['department_id'] = department_id
            await FSMAddGroup.next()
        else:
            await msg.answer('Помилка. Такої кафедри в базі даних не було знайдено.')


async def input_title_for_add_group(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'відміна':
        await state.finish()
        return

    async with state.proxy() as data:
        data['title'] = msg.text

        is_exist, group_id = await is_model_exist_by_name(msg, msg.text, class_model=Group)
        if is_exist:
            await msg.answer('Помилка. Група з такою назвою вже існує.')
        else:
            await msg.answer('Тепер відправте посилання на розклад групи з <a href="http://epi.kpi.ua">сайту</a>.')
            await FSMAddGroup.next()


async def input_url_schedule_for_add_group(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'відміна':
        await state.finish()
        return

    async with state.proxy() as data:
        data['url_schedule'] = msg.text

        if data.get('url_schedule', '').startswith('http://epi.kpi.ua'):
            pass
        else:
            await msg.answer('Посилання не є валідним чи направлено на сторонній сайт.')


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(start_add_new_group, commands=['add_group'], state=None)
    dp.register_message_handler(input_department_for_add_group, state=FSMAddGroup.department)
    dp.register_message_handler(input_title_for_add_group, state=FSMAddGroup.title)
    dp.register_message_handler(input_url_schedule_for_add_group, state=FSMAddGroup.url_schedule)
