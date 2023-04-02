from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Text, Command

from sqlalchemy.ext.asyncio import AsyncSession

from services.admin import (
    get_group_instance_by_id,
    change_title_for_group,
    delete_group,
    change_url_schedule_for_group,
    change_department_for_group
)
from services.utils import is_model_exist_by_name, is_user_admin, is_registered_user
from keyboards.kb_edit_group import get_keyboard_edit_group
from database.models import Department, Group

router = Router(name="fsm-edit-group-router")


class FSMEditGroup(StatesGroup):
    department = State()
    title = State()
    select_edit_group = State()
    input_edit_title = State()
    input_edit_department = State()
    input_edit_schedule_url = State()


@router.message(Command("edit_group"))
async def start_edit_group(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    if (
            await is_registered_user(msg, session=session) and
            await is_user_admin(msg, session=session)
    ):
        await state.set_state(FSMEditGroup.department)
        await msg.answer('Введіть назву кафедри, до якої належить група.')


@router.message(FSMEditGroup.department)
async def input_department_for_edit_group(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    await state.update_data(department_name=msg.text)

    is_exist, department_id = await is_model_exist_by_name(
        msg.text, class_model=Department, session=session
    )
    if is_exist:
        await msg.answer('Кафедра з такою назвою існує. Тепер введіть назву групи.')
        await state.update_data(department_id=department_id)
        await state.set_state(FSMEditGroup.title)
    else:
        await msg.answer('Помилка. Такої кафедри в базі даних не було знайдено.')


@router.message(FSMEditGroup.title)
async def input_title_for_edit_group(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    await state.update_data(title=msg.text)

    is_exist, group_id = await is_model_exist_by_name(
        msg.text, class_model=Group, session=session
    )
    if is_exist:
        data = await state.update_data(group_id=group_id)
        group = await get_group_instance_by_id(
            group_id=group_id, department_id=data['department_id'], session=session
        )
        await msg.answer(
            f'<b>Інформація про групу</b>\n'
            f'Факультет: {group.Department.Faculty.title} ({group.Department.Faculty.title_short})\n'
            f'Кафедра: {group.Department.title} ({group.Department.title_short})\n'
            f'Назва: {group.title}\n'
            f'Посилання на розклад: <a href="{group.schedule_url}">сайт</a>',
            reply_markup=get_keyboard_edit_group()
        )
        await state.set_state(FSMEditGroup.select_edit_group)
    else:
        await msg.answer('Помилка. Групи з такою назвою не існує.')


@router.callback_query(FSMEditGroup.select_edit_group)
@router.callback_query(F.data.startswith('group'))
async def group_edit_callback(
        callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    data_inline_keyboard = callback.data.split()

    match data_inline_keyboard:
        case 'group', 'change_title':
            await callback.message.edit_text(
                'Введіть нову назву для групи', reply_markup=None
            )
            await state.set_state(FSMEditGroup.input_edit_title)
        case 'group', 'change_department':
            await callback.message.edit_text(
                'Введіть назву нової кафедри для групи', reply_markup=None
            )
            await state.set_state(FSMEditGroup.input_edit_department)
        case 'group', 'change_url':
            await callback.message.edit_text(
                'Тепер відправте посилання на розклад групи з '
                '<a href="http://epi.kpi.ua">сайту</a>.', reply_markup=None
            )
            await state.set_state(FSMEditGroup.input_edit_schedule_url)
        case 'group', 'delete_group':
            await callback.message.edit_text(
                'Групу було видалено!', reply_markup=None
            )
            data = await state.get_data()
            await delete_group(
                group_id=data['group_id'],
                department_id=data['department_id'],
                session=session
            )
            await state.clear()

    await callback.answer()


@router.message(FSMEditGroup.input_edit_schedule_url)
async def input_new_url_schedule_for_edit_group(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.update_data(schedule_url=msg.text)

    if data.get('schedule_url', '').startswith('http://epi.kpi.ua'):
        await change_url_schedule_for_group(
            data['schedule_url'], group_id=data['group_id'], session=session
        )
        await msg.answer('Посилання було змінено і розклад скопійовано з сайту.')
        await state.clear()
    else:
        await msg.answer('Посилання не є валідним чи направлено на сторонній сайт.')


@router.message(FSMEditGroup.input_edit_title)
async def input_new_title_for_edit_group(
        msg: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.update_data(new_title=msg.text)
    await change_title_for_group(
        data['new_title'],
        group_id=data['group_id'],
        department_id=data['department_id'],
        session=session
    )
    await msg.answer(f'Назва групи була успішно змінена на {data["new_title"]}')
    await state.clear()


@router.message(FSMEditGroup.input_edit_department)
async def input_new_department_for_edit_group(
        msg: types.Message, state: FSMContext, session: AsyncSession
):
    await state.update_data(department_name=msg.text)

    is_exist, department_id = await is_model_exist_by_name(
        msg.text, class_model=Department, session=session
    )
    if is_exist:
        data = await state.get_data()
        data['new_department_id'] = department_id
        await change_department_for_group(
            data['new_department_id'],
            group_id=data['group_id'],
            department_id=data['department_id'],
            session=session
        )
        await msg.answer('Кафедру було успішно замінено!')
        await state.clear()
    else:
        await msg.answer('Помилка. Такої кафедри в базі даних не було знайдено.')
