from typing import Any
from aiogram import types
from sqlalchemy import select
from sqlalchemy.sql.selectable import Select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Group, Department, Faculty


async def is_user_admin(msg: types.Message) -> bool:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(User).where(User.id == msg.from_user.id)
        result = await session.execute(sql)
        user: User = result.scalars().first()

        if user is not None:
            return user.is_admin
        else:
            await msg.answer('Ви не зареєстровані в системі.')
            return False


async def get_or_create(session: AsyncSession, class_model: Any, sql: Select, **kwargs) -> (Any, bool):
    result = await session.execute(sql)
    instance = result.scalars().first()
    if instance is not None:
        return instance, False
    else:
        instance = class_model(**kwargs)
        await session.merge(instance)
        await session.commit()
        result = await session.execute(sql)
        instance = result.scalars().first()
        return instance, True


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