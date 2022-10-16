from aiogram import types, Dispatcher
from aiogram.utils.exceptions import BotBlocked
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database.models import Group
from services.other import get_information_all_users, is_registered_user, register_user, is_model_exist_by_name


async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    """Error handling (BotBlocked)"""
    print(f"Мене заблокував користувач!\nПовідомлення: {update}\nПомилка: {exception}")
    return True


async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand("help", "Інформація"),
    ])


async def get_text_messages(msg: types.Message):
    # await msg.answer('Я вас не розумію.')
    # await msg.answer('<a href="https://google.com">Kek</a>')
    print(f'{msg}')
    # sql = select(Group).filter(Group.title == 'ла-п11')
    if not await is_registered_user(msg):
        await msg.answer('Ви ще не зареєстровані. Будь ласка, введіть назву Вашої групи.')
        await FSMRegistration.group.set()
    else:
        match msg.text.lower():
            case 'тратата':
                information = await get_information_all_users(msg)
                # print(information)

            case 'сайт' | 'site':
                await msg.answer('<a href="http://epi.kpi.ua">Розклад КПІ</a>')

            case 'google' | 'гугл':
                await msg.answer('<a href="https://google.com">Посилання</a>')

            case 'розробник' | 'developer':
                await msg.answer('<b>Мій аккаунт: </b><a href="t.me/vladyslavtsurkan">Telegram</a>')

            case _:
                await msg.answer('Я вас не розумію.')


class FSMRegistration(StatesGroup):
    group = State()


async def input_name_group(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['group'] = msg.text

        is_exist, group_id = await is_model_exist_by_name(msg, data['group'], class_model=Group)

        if is_exist:
            if await register_user(msg, group_id):
                await msg.answer('Ви були успішно зареєстровані!')
                await state.finish()
            else:
                await msg.answer('На жаль, сталась помилка при реєстрації. Спробуйте ще раз ввести назву своєї групи.')
                await FSMRegistration.group.set()
        else:
            await msg.answer('Даної групи не було знайдено в базі даних. '
                             'Перевірте відправлений текст на помилки та спробуйте ще раз.')
            await FSMRegistration.group.set()


def register_handlers_other(dp: Dispatcher):
    dp.register_errors_handler(error_bot_blocked, exception=BotBlocked)
    dp.register_message_handler(input_name_group, state=FSMRegistration.group)
    dp.register_message_handler(get_text_messages, content_types=['text'])
