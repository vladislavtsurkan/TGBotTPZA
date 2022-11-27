from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from services.admin import (
    add_information_from_schedule_to_db,
    create_group,
    delete_group,
    is_group_exist_by_title_and_department_id
)
from services.utils import is_user_admin, is_model_exist_by_name
from database.models import Department, Group


class FSMAddGroup(StatesGroup):
    department = State()
    title = State()
    url_schedule = State()


async def start_add_new_group(msg: types.Message):
    if await is_user_admin(msg):
        await FSMAddGroup.department.set()
        await msg.answer('Введіть назву кафедри, до якої належить група.')


async def input_department_for_add_group(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['department_name'] = msg.text

        is_exist, department_id = await is_model_exist_by_name(
            msg.bot.get('db'), msg.text, class_model=Department
        )
        if is_exist:
            await msg.answer('Кафедра з такою назвою існує. Тепер введіть назву групи.')
            data['department_id'] = department_id
            await FSMAddGroup.next()
        else:
            await msg.answer('Помилка. Такої кафедри в базі даних не було знайдено.')


async def input_title_for_add_group(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = msg.text

        is_exist, _ = await is_group_exist_by_title_and_department_id(
            msg.bot.get('db'), data['title'], data['department_id']
        )
        if is_exist:
            await msg.answer('Помилка. Група з такою назвою на вказаній кафедрі вже існує.')
        else:
            await msg.answer(
                'Тепер відправте посилання на розклад групи з '
                '<a href="http://epi.kpi.ua">сайту</a>.'
            )
            await FSMAddGroup.next()


async def input_url_schedule_for_add_group(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_schedule'] = msg.text

        if data.get('url_schedule', '').startswith('http://epi.kpi.ua'):
            created_group: Group = await create_group(
                msg.bot.get('db'), data.get('department_id'), data.get('title'), data.get('url_schedule')
            )
            result = await add_information_from_schedule_to_db(msg.bot.get('db'), created_group)
            if result:
                await msg.answer('Група була створена і розклад скопійовано з сайту.')
            else:
                await msg.answer('Збір даних з сайту не вдався через проблеми в його роботі.')
                await delete_group(
                    msg.bot.get('db'), group_id=created_group.id,
                    department_id=created_group.department_id
                )
            await state.finish()
        else:
            await msg.answer('Посилання не є валідним чи направлено на сторонній сайт.')


def register_handlers_fsm_add_group(dp: Dispatcher):
    dp.register_message_handler(start_add_new_group, commands=['add_group'], state=None)
    dp.register_message_handler(input_department_for_add_group, state=FSMAddGroup.department)
    dp.register_message_handler(input_title_for_add_group, state=FSMAddGroup.title)
    dp.register_message_handler(input_url_schedule_for_add_group, state=FSMAddGroup.url_schedule)
