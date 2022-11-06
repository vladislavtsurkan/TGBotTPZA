from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_keyboard_edit_group(*, department_id: int, group_id: int) -> InlineKeyboardMarkup:
    keyboard_edit_group = InlineKeyboardMarkup(row_width=2)
    keyboard_edit_group.add(InlineKeyboardButton(text='Змінити кафедру',
                                                 callback_data=f'group change_department {department_id} {group_id}'),
                            InlineKeyboardButton(text='Змінити назву',
                                                 callback_data=f'group change_title {department_id} {group_id}'),
                            InlineKeyboardButton(text='Змінити посилання',
                                                 callback_data=f'group change_url {department_id} {group_id}'),
                            InlineKeyboardButton(text='Видалити групу',
                                                 callback_data=f'group delete_group {department_id} {group_id}'),
                            )

    return keyboard_edit_group
