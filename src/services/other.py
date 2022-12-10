from aiogram import types
from sqlalchemy import select

from src.database.models import User, Group, Faculty, Department


async def get_information_all_users(msg: types.Message) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(User, Group, Department, Faculty).where(
            User.group_id == Group.id, Department.id == Group.department_id,
            Faculty.id == Department.faculty_id
        )

        result = await session.execute(sql)
        users = result.scalars()

        for user in users:
            print(f'{user.id} / {user.Group.title} / {user.Group.Department.title} / '
                  f'{user.Group.Department.Faculty.title}')
