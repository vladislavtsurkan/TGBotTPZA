from aiogram import types
from sqlalchemy import select

from database.models import User, Group, Faculty, Department


async def is_registered_user(msg: types.Message) -> bool:
    ids_skip: set = msg.bot.get('ids_skip_check_registered')

    if (id_user := msg.from_user.id) in ids_skip:
        return True

    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(User).where(User.id == id_user)
        result = await session.execute(sql)
        user = result.scalars().first()

        if user is not None:
            ids_skip.add(id_user)
            msg.bot['ids_skip_check_registered'] = ids_skip
            return True
        else:
            return False


async def is_model_exist_by_name(msg: types.Message, title: str, *,
                                 class_model: type(Group) | type(Department) | type(Faculty)) -> (bool, int):
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(class_model).where(class_model.title == title)
        result = await session.execute(sql)
        instance_model = result.scalars().first()
        return (is_not_none := instance_model is not None), instance_model.id if is_not_none else 0


async def register_user(msg: types.Message, group_id: int) -> bool:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        try:
            await session.merge(
                User(id=msg.from_user.id, group_id=group_id, is_admin=False)
            )
            await session.commit()
        except Exception:
            return False
        else:
            return True


async def get_information_all_users(msg: types.Message) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(User, Group, Department, Faculty).where(User.group_id == Group.id,
                                                             Department.id == Group.department_id,
                                                             Faculty.id == Department.faculty_id)

        result = await session.execute(sql)
        users = result.scalars()

        for user in users:
            print(f'{user.id} / {user.Group.title} / {user.Group.Department.title} / '
                  f'{user.Group.Department.Faculty.title}')
