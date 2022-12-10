from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_keyboard_edit_faculty() -> InlineKeyboardMarkup:
    keyboard_edit_faculty = InlineKeyboardMarkup(row_width=2)
    keyboard_edit_faculty.add(
        InlineKeyboardButton(text='Змінити назву', callback_data='faculty change_title'),
        InlineKeyboardButton(text='Видалити факультет', callback_data='faculty delete_faculty'),
    )

    return keyboard_edit_faculty
