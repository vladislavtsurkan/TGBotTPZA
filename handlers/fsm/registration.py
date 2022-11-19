from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from services.admin import register_user, get_groups_by_title
from keyboards.kb_with_groups import get_keyboard_with_groups
from database.models import Group


class FSMRegistration(StatesGroup):
    group = State()
    department = State()


async def input_name_group(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['group'] = msg.text

        groups: list[Group] = await get_groups_by_title(msg, data['group'])
        match len(groups):
            case 0:
                await msg.answer('Даної групи не було знайдено в базі даних. '
                                 'Перевірте відправлений текст на помилки та спробуйте ще раз.')
            case 1:
                group: Group = groups[0]
                if await register_user(msg, group.id):
                    await msg.answer('Ви були успішно зареєстровані!')
                    await state.finish()
                else:
                    await msg.answer('На жаль, сталась помилка при реєстрації. '
                                     'Спробуйте ще раз ввести назву своєї групи.')
            case _:
                await msg.answer('<b>Оберіть свою кафедру серед зазначених нижче:</b>',
                                 reply_markup=get_keyboard_with_groups(groups))
                await FSMRegistration.next()


async def group_select_callback(callback: types.CallbackQuery, state: FSMContext):
    data_inline_keyboard = callback.data.split()
    group_id = int(data_inline_keyboard[2])

    if await register_user(callback, group_id):
        await callback.message.edit_text('Ви були успішно зареєстровані!', reply_markup=None)
    else:
        await callback.message.edit_text('На жаль, сталась помилка при реєстрації.', reply_markup=None)
    await state.finish()
    await callback.answer()


def register_handlers_fsm_registration(dp: Dispatcher):
    dp.register_message_handler(input_name_group, state=FSMRegistration.group)
    dp.register_callback_query_handler(group_select_callback, Text(startswith='group select'),
                                       state=FSMRegistration.department)
