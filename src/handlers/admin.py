from aiogram import types, Router
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from services.admin import try_register_first_admin
from services.utils import is_registered_user, is_user_admin

_admin_commands = """
<b>👨‍💻 Команди адміністратора:</b>

/cmds - список команд
/add_faculty - додати факультет
/edit_faculty - редагувати факультет
/add_department - додати кафедру
/edit_department - редагувати кафедру
/add_group - додати групу
/edit_group - редагувати групу
"""

router = Router(name="admin-commands")


@router.message(Command("cmds"))
async def get_admin_commands(msg: types.Message, session: AsyncSession) -> None:
    if (
            await is_registered_user(msg, session=session) and
            await is_user_admin(msg, session=session)
    ):
        await msg.answer(_admin_commands)


@router.message(Command("get_admin"))
async def register_first_admin(msg: types.Message, session: AsyncSession) -> None:
    if await try_register_first_admin(user_id=msg.from_user.id, session=session):
        await msg.answer('Ви успішно отримали права адміністратора.')
