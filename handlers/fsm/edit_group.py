from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from services.admin import get_information_group
from services.utils import is_user_admin, is_model_exist_by_name
from keyboards.kb_edit_group import get_keyboard_edit_group
from database.models import Department, Group


class FSMDeleteGroup(StatesGroup):
    department = State()
    title = State()


async def start_edit_group(msg: types.Message):
    if await is_user_admin(msg):
        await FSMDeleteGroup.department.set()
        await msg.answer('Введіть назву кафедри, до якої належить група.')


async def input_department_for_edit_group(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['department_name'] = msg.text

        is_exist, department_id = await is_model_exist_by_name(msg, msg.text, class_model=Department)
        if is_exist:
            await msg.answer('Кафедра з такою назвою існує. Тепер введіть назву групи.')
            data['department_id'] = department_id
            await FSMDeleteGroup.next()
        else:
            await msg.answer('Помилка. Такої кафедри в базі даних не було знайдено.')


async def input_title_for_edit_group(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = msg.text

        is_exist, group_id = await is_model_exist_by_name(msg, msg.text, class_model=Group)
        if is_exist:
            group = await get_information_group(msg, group_id=group_id, department_id=data['department_id'])
            await msg.answer(f'<b>Інформація про групу</b>\n'
                             f'Факультет: {group.Department.Faculty.title} ({group.Department.Faculty.title_short})\n'
                             f'Кафедра: {group.Department.title} ({group.Department.title_short})\n'
                             f'Назва: {group.title}\n'
                             f'Посилання на розклад: <a href="{group.schedule_url}">сайт</a>',
                             reply_markup=get_keyboard_edit_group(department_id=group.department_id, group_id=group.id))
            await state.finish()
        else:
            await msg.answer('Помилка. Групи з такою назвою не існує.')


def register_handlers_fsm_edit_group(dp: Dispatcher):
    dp.register_message_handler(start_edit_group, commands=['edit_group'], state=None)
    dp.register_message_handler(input_department_for_edit_group, state=FSMDeleteGroup.department)
    dp.register_message_handler(input_title_for_edit_group, state=FSMDeleteGroup.title)
