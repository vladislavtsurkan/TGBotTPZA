from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from services.admin import (
    get_group_instance_by_id, change_title_group, delete_group, change_url_schedule_group,
    change_department_for_group
)
from services.utils import is_user_admin, is_model_exist_by_name
from keyboards.kb_edit_group import get_keyboard_edit_group
from database.models import Department, Group


class FSMEditGroup(StatesGroup):
    department = State()
    title = State()
    select_edit_group = State()
    input_edit_title = State()
    input_edit_department = State()
    input_edit_schedule_url = State()


async def start_edit_group(msg: types.Message) -> None:
    if await is_user_admin(msg):
        await FSMEditGroup.department.set()
        await msg.answer('Введіть назву кафедри, до якої належить група.')


async def input_department_for_edit_group(msg: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['department_name'] = msg.text

        is_exist, department_id = await is_model_exist_by_name(
            msg.bot.get('db'), msg.text, class_model=Department
        )
        if is_exist:
            await msg.answer('Кафедра з такою назвою існує. Тепер введіть назву групи.')
            data['department_id'] = department_id
            await FSMEditGroup.next()
        else:
            await msg.answer('Помилка. Такої кафедри в базі даних не було знайдено.')


async def input_title_for_edit_group(msg: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['title'] = msg.text

        is_exist, group_id = await is_model_exist_by_name(
            msg.bot.get('db'), msg.text, class_model=Group
        )
        if is_exist:
            data['group_id'] = group_id
            group = await get_group_instance_by_id(
                msg.bot.get('db'), group_id=group_id, department_id=data['department_id']
            )
            await msg.answer(
                f'<b>Інформація про групу</b>\n'
                f'Факультет: {group.Department.Faculty.title} ({group.Department.Faculty.title_short})\n'
                f'Кафедра: {group.Department.title} ({group.Department.title_short})\n'
                f'Назва: {group.title}\n'
                f'Посилання на розклад: <a href="{group.schedule_url}">сайт</a>',
                reply_markup=get_keyboard_edit_group()
            )
            await FSMEditGroup.next()
        else:
            await msg.answer('Помилка. Групи з такою назвою не існує.')


async def group_edit_callback(callback: types.CallbackQuery, state: FSMContext):
    data_inline_keyboard = callback.data.split()
    print(data_inline_keyboard)
    async with state.proxy() as data:
        match data_inline_keyboard:
            case 'group', 'change_title':
                await callback.message.edit_text(
                    'Введіть нову назву для групи', reply_markup=None
                )
                await FSMEditGroup.input_edit_title.set()
            case 'group', 'change_department':
                await callback.message.edit_text(
                    'Введіть назву нової кафедри для групи', reply_markup=None
                )
                await FSMEditGroup.input_edit_department.set()
            case 'group', 'change_url':
                await callback.message.edit_text(
                    'Тепер відправте посилання на розклад групи з '
                    '<a href="http://epi.kpi.ua">сайту</a>.', reply_markup=None
                )
                await FSMEditGroup.input_edit_schedule_url.set()
            case 'group', 'delete_group':
                await callback.message.edit_text(
                    'Групу було видалено!', reply_markup=None
                )
                await delete_group(
                    callback.bot.get('db'), group_id=data['group_id'],
                    department_id=data['department_id']
                )
                await state.finish()

    await callback.answer()


async def input_new_url_schedule_for_edit_group(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['schedule_url'] = msg.text

        if data.get('schedule_url', '').startswith('http://epi.kpi.ua'):
            await change_url_schedule_group(
                msg.bot.get('db'), data['schedule_url'], group_id=data['group_id']
            )
            await msg.answer('Посилання було змінено і розклад скопійовано з сайту.')
            await state.finish()
        else:
            await msg.answer('Посилання не є валідним чи направлено на сторонній сайт.')


async def input_new_title_for_edit_group(msg: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['new_title'] = msg.text
        await change_title_group(
            msg.bot.get('db'), data['new_title'], group_id=data['group_id'],
            department_id=data['department_id']
        )
        await msg.answer(f'Назва групи була успішно змінена на {data["new_title"]}')
        await state.finish()


async def input_new_department_for_edit_group(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['department_name'] = msg.text

        is_exist, department_id = await is_model_exist_by_name(
            msg.bot.get('db'), msg.text, class_model=Department
        )
        if is_exist:
            data['new_department_id'] = department_id
            await change_department_for_group(
                msg.bot.get('db'), data['new_department_id'], group_id=data['group_id'],
                department_id=data['department_id']
            )
            await msg.answer('Кафедру було успішно замінено!')
            await state.finish()
        else:
            await msg.answer('Помилка. Такої кафедри в базі даних не було знайдено.')


def register_handlers_fsm_edit_group(dp: Dispatcher):
    dp.register_message_handler(start_edit_group, commands=['edit_group'], state=None)
    dp.register_message_handler(input_department_for_edit_group, state=FSMEditGroup.department)
    dp.register_message_handler(input_title_for_edit_group, state=FSMEditGroup.title)
    dp.register_callback_query_handler(
        group_edit_callback, Text(startswith='group'), state=FSMEditGroup.select_edit_group
    )
    dp.register_message_handler(
        input_new_title_for_edit_group, state=FSMEditGroup.input_edit_title
    )
    dp.register_message_handler(
        input_new_url_schedule_for_edit_group, state=FSMEditGroup.input_edit_schedule_url
    )
    dp.register_message_handler(
        input_new_department_for_edit_group, state=FSMEditGroup.input_edit_department
    )
