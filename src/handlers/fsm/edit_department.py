from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from services.admin import (
    get_department_instance_by_title, change_faculty_for_department, delete_department,
    change_title_for_department
)
from services.utils import is_model_exist_by_name
from handlers.fsm.decorators import check_user_is_admin, check_user_is_registered
from keyboards.kb_edit_department import get_keyboard_edit_department
from database.models import Department, Faculty


class FSMEditDepartment(StatesGroup):
    title = State()
    select_edit_department = State()
    input_edit_title = State()
    input_edit_title_short = State()
    input_edit_faculty = State()


@check_user_is_registered
@check_user_is_admin
async def start_edit_department(msg: types.Message) -> None:
    await FSMEditDepartment.title.set()
    await msg.answer('Введіть назву кафедри.')


async def input_title_for_edit_department(msg: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['title'] = msg.text

        department_instance: Department = await get_department_instance_by_title(
            msg.bot.get('db'), msg.text
        )
        if department_instance:
            await msg.answer(
                f'<b>Інформація про кафедру</b>\n'
                f'Факультет: {department_instance.Faculty.title} ({department_instance.Faculty.title_short})\n'
                f'Кафедра: {department_instance.title} ({department_instance.title_short})',
                reply_markup=get_keyboard_edit_department()
            )
            data['department_id'] = department_instance.id
            await FSMEditDepartment.next()
        else:
            await msg.answer('Помилка. Такої кафедри в базі даних не було знайдено.')


async def department_edit_callback(callback: types.CallbackQuery, state: FSMContext):
    data_inline_keyboard = callback.data.split()

    async with state.proxy() as data:
        match data_inline_keyboard:
            case 'department', 'change_title':
                await callback.message.edit_text(
                    'Введіть нову назву для кафедри.', reply_markup=None
                )
                await FSMEditDepartment.input_edit_title.set()
            case 'department', 'change_faculty':
                await callback.message.edit_text(
                    'Введіть назву нового факультету для кафедри.', reply_markup=None
                )
                await FSMEditDepartment.input_edit_faculty.set()
            case 'department', 'delete_department':
                await callback.message.edit_text(
                    'Кафедру разом зі зв\'язаними групами було видалено!',
                    reply_markup=None
                )
                await delete_department(callback.bot.get('db'), department_id=data['department_id'])
                await state.finish()

    await callback.answer()


async def input_new_title_for_edit_department(msg: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['new_title'] = msg.text
        await msg.answer(f'Тепер введіть нову абревіатуру для кафедри.')
        await FSMEditDepartment.input_edit_title_short.set()


async def input_new_title_short_for_edit_department(msg: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['new_title_short'] = msg.text
        await msg.answer(f'Назва кафедри була змінена на: {data["new_title"]} ({data["new_title_short"]})')
        await change_title_for_department(
            msg.bot.get('db'), department_id=data['department_id'], title=data['new_title'],
            title_short=data['new_title_short']
        )
        await state.finish()


async def input_new_faculty_for_edit_department(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['department_name'] = msg.text

        is_exist, faculty_id = await is_model_exist_by_name(
            msg.bot.get('db'), msg.text, class_model=Faculty
        )
        if is_exist:
            data['new_faculty_id'] = faculty_id
            await change_faculty_for_department(
                msg.bot.get('db'), department_id=data['department_id'],
                faculty_id=data['new_faculty_id']
            )
            await msg.answer('Факультет було успішно замінено!')
            await state.finish()
        else:
            await msg.answer('Помилка. Такого факультету в базі даних не було знайдено.')


def register_handlers_fsm_edit_department(dp: Dispatcher):
    dp.register_message_handler(start_edit_department, commands=['edit_department'], state=None)
    dp.register_message_handler(input_title_for_edit_department, state=FSMEditDepartment.title)
    dp.register_callback_query_handler(
        department_edit_callback, Text(startswith='department'),
        state=FSMEditDepartment.select_edit_department
    )
    dp.register_message_handler(
        input_new_title_for_edit_department, state=FSMEditDepartment.input_edit_title
    )
    dp.register_message_handler(
        input_new_title_short_for_edit_department, state=FSMEditDepartment.input_edit_title_short
    )
    dp.register_message_handler(
        input_new_faculty_for_edit_department, state=FSMEditDepartment.input_edit_faculty
    )
