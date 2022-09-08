from aiogram import types, Dispatcher


async def send_welcome(msg: types.Message):
    await msg.answer(f'Я бот-помічник для групи ЛА-п11 (ТПЗА, ІХФ). Приємно познайомитись, '
                     f'{msg.from_user.first_name}.\n'
                     f'Поки що я нічого не вмію.')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
