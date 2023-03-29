from typing import Type
from datetime import date

from aiogram import types
from sqlalchemy import select
from sqlalchemy.sql.selectable import Select
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import get_session_db
from database.models import Base, User, Group, Department, Faculty


async def get_or_create(
        session: AsyncSession, class_model: Type[Base], sql: Select, **kwargs
) -> (Type[Base], bool):
    """Get or create model by class_model and sql for search instance"""
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


async def is_model_exist_by_name(
        title: str, *, class_model: Type[Group | Department | Faculty]
) -> (bool, int):
    """Check if model exist by title (work with Group, Department, Faculty)"""
    session = await get_session_db()

    sql = select(class_model).where(class_model.title == title)
    result = await session.execute(sql)
    instance_model = result.scalars().first()
    return (
        is_not_none := (instance_model is not None),
        instance_model.id if is_not_none else 0
    )


async def is_user_admin(msg: types.Message) -> bool:
    """Check if user is admin"""
    session = await get_session_db()

    sql = select(User).where(User.id == msg.from_user.id)
    result = await session.execute(sql)
    user: User = result.scalars().first()

    if user is not None:
        return user.is_admin
    else:
        return False


async def is_registered_user(msg: types.Message) -> bool:
    """Check if user is registered in database"""
    ids_skip: set[int] = msg.bot.get('ids_skip_check_registered')

    if (id_user := msg.from_user.id) in ids_skip:
        return True

    session = await get_session_db()

    sql = select(User).where(User.id == id_user)
    result = await session.execute(sql)
    user = result.scalars().first()

    if user is not None:
        ids_skip.add(id_user)
        msg.bot['ids_skip_check_registered'] = ids_skip
        return True
    else:
        return False


def get_current_week_number() -> int:
    """Get current week number of schedule (1 or 2)"""
    today = date.today()
    week_number = today.isocalendar()[1]
    if week_number < 36:
        week_number += 36

    return week_number % 2 + 1


def get_time_of_lesson_by_number(lesson_number: int) -> str:
    """Get time of lesson by number"""
    return {
        1: '8:30-10:05',
        2: '10:25-12:00',
        3: '12:20-13:55',
        4: '14:15-15:50',
        5: '16:10-17:45',
        6: '18:05-19:40',
        7: '19:50-21:25',
    }[lesson_number]


def get_day_of_week_by_number(day_number: int) -> str:
    """Get day of week by number"""
    return {
        1: 'Понеділок',
        2: 'Вівторок',
        3: 'Середа',
        4: 'Четвер',
        5: 'П\'ятниця',
        6: 'Субота',
        7: 'Неділя'
    }[day_number]


def get_current_day_and_week_of_schedule_number(
        *, is_tomorrow: bool = False
) -> (int, int):
    """Get current day and week number (1-7 and 1 or 2)"""
    day_of_week_number = date.today().weekday() + (2 if is_tomorrow else 1)
    week_of_schedule_number = get_current_week_number()

    if day_of_week_number > 7:
        day_of_week_number = 1
        week_of_schedule_number = 1 if week_of_schedule_number == 2 else 2

    return day_of_week_number, week_of_schedule_number
