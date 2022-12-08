from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from services.admin import get_faculty_instance_by_title, change_title_for_faculty, delete_faculty
from services.utils import check_if_user_is_admin
from keyboards.kb_edit_faculty import get_keyboard_edit_faculty
from database.models import Faculty


class FSMEditFaculty(StatesGroup):
    title = State()
    select_edit_faculty = State()
    input_edit_title = State()
    input_edit_title_short = State()


@check_if_user_is_admin
async def start_edit_faculty(msg: types.Message) -> None:
    await FSMEditFaculty.title.set()
    await msg.answer('Введіть назву факультета.')


async def input_title_for_edit_faculty(msg: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['title'] = msg.text

        faculty_instance: Faculty = await get_faculty_instance_by_title(msg.bot.get('db'), msg.text)
        if faculty_instance:
            await msg.answer(
                f'<b>Інформація про факультет</b>\n'
                f'Факультет: {faculty_instance.title} ({faculty_instance.title_short})',
                reply_markup=get_keyboard_edit_faculty()
            )
            data['faculty_id'] = faculty_instance.id
            await FSMEditFaculty.next()
        else:
            await msg.answer('Помилка. Такого факультету в базі даних не було знайдено.')


async def faculty_edit_callback(callback: types.CallbackQuery, state: FSMContext):
    data_inline_keyboard = callback.data.split()

    async with state.proxy() as data:
        match data_inline_keyboard:
            case 'faculty', 'change_title':
                await callback.message.edit_text(
                    'Введіть нову назву для факультета.', reply_markup=None
                )
                await FSMEditFaculty.input_edit_title.set()
            case 'faculty', 'delete_faculty':
                await callback.message.edit_text(
                    'Факультет разом зі зв\'язаними кафедрами та групами було видалено!',
                    reply_markup=None
                )
                await delete_faculty(callback.bot.get('db'), faculty_id=data['faculty_id'])
                await state.finish()

    await callback.answer()


async def input_new_title_for_edit_faculty(msg: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['new_title'] = msg.text
        await msg.answer(f'Тепер введіть нову абревіатуру для факультета.')
        await FSMEditFaculty.input_edit_title_short.set()


async def input_new_title_short_for_edit_faculty(msg: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['new_title_short'] = msg.text
        await msg.answer(
            f'Назва факультету була змінена на: {data["new_title"]} ({data["new_title_short"]})'
        )
        await change_title_for_faculty(
            msg.bot.get('db'), faculty_id=data['faculty_id'], title=data['new_title'],
            title_short=data['new_title_short']
        )
        await state.finish()


def register_handlers_fsm_edit_faculty(dp: Dispatcher):
    dp.register_message_handler(start_edit_faculty, commands=['edit_faculty'], state=None)
    dp.register_message_handler(input_title_for_edit_faculty, state=FSMEditFaculty.title)
    dp.register_callback_query_handler(
        faculty_edit_callback, Text(startswith='faculty'),
        state=FSMEditFaculty.select_edit_faculty
    )
    dp.register_message_handler(
        input_new_title_for_edit_faculty, state=FSMEditFaculty.input_edit_title
    )
    dp.register_message_handler(
        input_new_title_short_for_edit_faculty, state=FSMEditFaculty.input_edit_title_short
    )
