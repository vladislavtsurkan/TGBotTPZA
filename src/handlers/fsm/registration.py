from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from services.admin import get_groups_instances_by_title
from services.other import register_user
from keyboards.kb_with_groups import get_keyboard_with_groups
from database.models import Group

router = Router(name="fsm-registration-router")


class FSMRegistration(StatesGroup):
    group = State()
    department = State()


async def start_registration(msg: types.Message, state: FSMContext) -> None:
    await msg.answer('Введіть назву Вашої групи.')
    await state.set_state(FSMRegistration.group)


@router.message(FSMRegistration.group)
async def input_name_group(msg: types.Message, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(group=msg.text)

    groups: list[Group] = await get_groups_instances_by_title(msg.text, session=session)
    match len(groups):
        case 0:
            await msg.answer(
                'Даної групи не було знайдено в базі даних. '
                'Перевірте відправлений текст на помилки та спробуйте ще раз.'
            )
        case 1:
            group: Group = groups[0]
            if await register_user(group.id, user_id=msg.from_user.id, session=session):
                await msg.answer('Налаштування групи були успішно збережені.')
                await state.clear()
            else:
                await msg.answer('На жаль, сталась помилка. '
                                 'Спробуйте ще раз ввести назву своєї групи.')
        case _:
            await msg.answer('<b>Оберіть свою кафедру серед зазначених нижче:</b>',
                             reply_markup=get_keyboard_with_groups(groups))
            await state.set_state(FSMRegistration.department)


@router.callback_query(FSMRegistration.department)
@router.callback_query(F.data.startswith('group select'))
async def group_select_callback(
        callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    data_inline_keyboard = callback.data.split()
    group_id = int(data_inline_keyboard[2])

    if await register_user(group_id, user_id=callback.from_user.id, session=session):
        await callback.message.edit_text(
            'Чудово. Тепер Ви можете користуватись повним функціоналом.', reply_markup=None
        )
    else:
        await callback.message.edit_text(
            'На жаль, сталась помилка при запису даних.', reply_markup=None
        )
    await state.clear()
    await callback.answer()
