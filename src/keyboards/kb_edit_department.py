from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_keyboard_edit_department() -> InlineKeyboardMarkup:
    keyboard_edit_department = InlineKeyboardMarkup(row_width=2)
    keyboard_edit_department.add(
        InlineKeyboardButton(text='Змінити факультет', callback_data='department change_faculty'),
        InlineKeyboardButton(text='Змінити назву', callback_data='department change_title'),
        InlineKeyboardButton(text='Видалити кафедру', callback_data='department delete_department'),
    )

    return keyboard_edit_department
