from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from services.admin import just_def
from keyboards.kb_edit_group import get_keyboard_edit_group


async def test(msg: types.Message):
    await just_def(msg)


async def group_edit_callback(callback: types.CallbackQuery):
    data = callback.data.split()
    print(data)
    await callback.answer('ok')
    match data:
        case 'group', 'change_title', department_id, group_id:
            print(f'Змінюємо назву групі №{group_id}, кафедри №{department_id}')
        case 'group', 'change_department', department_id, group_id:
            print(f'Змінюємо кафедру групі №{group_id}, кафедри №{department_id}')
        case 'group', 'change_url', department_id, group_id:
            print(f'Змінюємо посилання на розклад групі №{group_id}, кафедри №{department_id}')
        case 'group', 'delete_group', department_id, group_id:
            print(f'Видаляємо групу №{group_id}, кафедри №{department_id}')

    # await callback.message.delete()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(test, commands=['test'])
    dp.register_callback_query_handler(group_edit_callback, Text(startswith='group'))
