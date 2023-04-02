from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_keyboard_edit_group() -> InlineKeyboardMarkup:
    keyboard_edit_group = InlineKeyboardMarkup(row_width=2)
    keyboard_edit_group.inline_keyboard.append(
        [
            InlineKeyboardButton(text='Змінити кафедру', callback_data='group change_department'),
            InlineKeyboardButton(text='Змінити назву', callback_data='group change_title'),
            InlineKeyboardButton(text='Змінити посилання', callback_data='group change_url'),
            InlineKeyboardButton(text='Видалити групу', callback_data='group delete_group'),
        ]
    )

    return keyboard_edit_group
