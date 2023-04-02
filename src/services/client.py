from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Group, Lesson, Discipline, Teacher
from services.utils import (
    get_time_of_lesson_by_number,
    get_day_of_week_by_number,
    get_current_day_and_week_of_schedule_number
)


async def get_lessons_current_or_next_week_for_user(
        *, group_id: int, next_week: bool = False, session: AsyncSession
) -> str:
    """Get lessons for user current or next week"""
    group_title, lessons = await _get_group_title_and_lessons_by_group_id(session, group_id)
    _, week_of_schedule_number = get_current_day_and_week_of_schedule_number()

    if next_week:
        week_of_schedule_number = 1 if week_of_schedule_number == 2 else 2

    current_lessons_id = [lesson.id for lesson in lessons if lesson.week == week_of_schedule_number]
    sql_lessons = select(Lesson, Discipline).where(
        Lesson.discipline_id == Discipline.id,
        Lesson.id.in_(current_lessons_id),
        Lesson.week == week_of_schedule_number
    ).options(joinedload(Lesson.Discipline)).order_by(Lesson.day, Lesson.number_lesson)
    result = await session.execute(sql_lessons)
    current_lessons = tuple(result.scalars())

    sorted_lessons = [
        tuple(filter(lambda lesson: lesson.day == i, current_lessons)) for i in range(1, 8)
    ]

    answer = (
        f'<b>Пари {"наступного" if next_week else "поточного"} тижня '
        f'у групи {group_title}:</b>\n\n'
    )
    for day, day_lessons in enumerate(sorted_lessons, 1):
        if day_lessons:
            day_of_week = get_day_of_week_by_number(day)
            answer += f'<em><b>{day_of_week}:</b></em>\n'
            for lesson in day_lessons:
                teachers: Iterable[Teacher] = await session.run_sync(
                    lambda _: lesson.teachers
                )
                answer += (
                        f'<b>[{lesson.number_lesson}]</b> <em>{lesson.Discipline.title}</em>\n' +
                        (f'<em>{", ".join(teacher.full_name for teacher in teachers)}</em>\n'
                         if teachers else '')
                )
            answer += '\n'

    return answer


async def get_lessons_today_or_tomorrow_for_user(
        *, group_id: int, tomorrow: bool = False, session: AsyncSession
) -> str:
    """Get lessons for user today or tomorrow"""
    group_title, lessons = await _get_group_title_and_lessons_by_group_id(session, group_id)

    day_of_week_number, week_of_schedule_number = get_current_day_and_week_of_schedule_number(
        is_tomorrow=tomorrow
    )

    current_lessons_id = [
        lesson.id for lesson in lessons
        if lesson.day == day_of_week_number and lesson.week == week_of_schedule_number
    ]

    sql_lessons = select(Lesson, Discipline).where(
        Lesson.discipline_id == Discipline.id,
        Lesson.day == day_of_week_number,
        Lesson.id.in_(current_lessons_id),
        Lesson.week == week_of_schedule_number
    ).options(joinedload(Lesson.Discipline)).order_by(Lesson.number_lesson)
    result = await session.execute(sql_lessons)
    current_lessons = tuple(result.scalars())

    current_day = "завтра" if tomorrow else "сьогодні"
    if len(current_lessons) == 0:
        return (
            f'<b>У групи <em>{group_title}</em> {current_day} немає пар</b>'
        )

    answer = (
        f'<b>Пари {"завтра" if tomorrow else "сьогодні"} '
        f'у групи {group_title}:</b>\n\n'
    )
    for lesson in current_lessons:
        teachers: Iterable[Teacher] = await session.run_sync(
            lambda _: lesson.teachers
        )
        lesson_time = get_time_of_lesson_by_number(lesson.number_lesson)
        answer += (
                f'<b>[{lesson.number_lesson}] <em>[{lesson_time}]</em></b> '
                f'<em>{lesson.Discipline.title}</em>\n' +
                (f'<em>{", ".join(teacher.full_name for teacher in teachers)}</em>\n'
                 if teachers else '') +
                (f'<em><b>Інформація:</b> {lesson.type_and_location}</em>\n\n'
                 if lesson.type_and_location != "Немає інформації" else '\n')
        )

    return answer


async def get_group_id_by_user_id(*, user_id: int, session: AsyncSession) -> int:
    """Get group id by user id"""
    sql_user = select(User).where(User.id == user_id)
    result = await session.execute(sql_user)
    user = result.scalars().first()
    return user.group_id


async def _get_group_title_and_lessons_by_group_id(
        session: AsyncSession, group_id: int
) -> (str, Iterable[Lesson]):
    """Get group title and lessons by group id"""
    sql = select(Group).where(
        Group.id == group_id
    )
    result = await session.execute(sql)
    group_instance: Group = result.scalars().first()

    lessons: Iterable[Lesson] = await session.run_sync(
        lambda _: group_instance.lessons
    )
    return group_instance.title, lessons
