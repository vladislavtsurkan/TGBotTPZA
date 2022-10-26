from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from services.utils import is_model_exist_by_name
from services.admin import register_user
from database.models import Group


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
        else:
            await msg.answer('Даної групи не було знайдено в базі даних. '
                             'Перевірте відправлений текст на помилки та спробуйте ще раз.')


def register_handlers_fsm_registration(dp: Dispatcher):
    dp.register_message_handler(input_name_group, state=FSMRegistration.group)
