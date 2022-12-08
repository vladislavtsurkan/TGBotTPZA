from typing import Iterable
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Group, Lesson, Discipline, Teacher

days_of_week = ('Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П\'ятниця', 'Субота', 'Неділя')


async def get_lessons_current_or_next_week_for_user(
        db_session: sessionmaker, *, user_id: int, week: int, next_week=False
) -> str:
    async with db_session() as session:
        user_instance, lessons = await _get_user_instance_and_lessons_by_user_id(session, user_id)

        if next_week:
            week = 1 if week == 2 else 2

        current_lessons_id = [lesson.id for lesson in lessons if lesson.week == week]
        sql_lessons = select(Lesson, Discipline).where(
            Lesson.discipline_id == Discipline.id,
            Lesson.id.in_(current_lessons_id),
            Lesson.week == week
        ).options(joinedload(Lesson.Discipline)).order_by(Lesson.day, Lesson.number_lesson)
        result = await session.execute(sql_lessons)
        current_lessons = tuple(result.scalars())

        sorted_lessons = [
            tuple(filter(lambda lesson: lesson.day == i, current_lessons)) for i in range(1, 8)
        ]

        answer = (
            f'<b>Пари {"наступного" if next_week else "поточного"} тижня '
            f'у групи {user_instance.Group.title}:</b>\n\n'
        )
        for day, day_lessons in enumerate(sorted_lessons, 1):
            if day_lessons:
                answer += f'<em><b>{days_of_week[day - 1]}:</b></em>\n'
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
        db_session: sessionmaker, *, user_id: int, week: int, tomorrow=False
) -> str:
    async with db_session() as session:
        user_instance, lessons = await _get_user_instance_and_lessons_by_user_id(session, user_id)

        day_of_week = date.today().weekday() + (2 if tomorrow else 1)
        if day_of_week > 7:
            day_of_week = 1
            week = 1 if week == 2 else 2

        current_lessons_id = [
            lesson.id for lesson in lessons if lesson.day == day_of_week and lesson.week == week
        ]

        sql_lessons = select(Lesson, Discipline).where(
            Lesson.discipline_id == Discipline.id,
            Lesson.day == day_of_week,
            Lesson.id.in_(current_lessons_id),
            Lesson.week == week
        ).options(joinedload(Lesson.Discipline)).order_by(Lesson.number_lesson)
        result = await session.execute(sql_lessons)
        current_lessons = result.scalars()

        answer = (
            f'<b>Пари {"завтра" if tomorrow else "сьогодні"} '
            f'у групи {user_instance.Group.title}:</b>\n\n'
        )
        for lesson in current_lessons:
            teachers: Iterable[Teacher] = await session.run_sync(
                lambda _: lesson.teachers
            )
            answer += (
                f'<b>[{lesson.number_lesson}]</b> <em>{lesson.Discipline.title}</em>\n' +
                (f'<em>{", ".join(teacher.full_name for teacher in teachers)}</em>\n'
                 if teachers else '') +
                (f'<em><b>Інформація:</b> {lesson.type_and_location}</em>\n\n'
                 if lesson.type_and_location != "Немає інформації" else '\n')
            )

        return answer


async def _get_user_instance_and_lessons_by_user_id(
        session: AsyncSession, user_id: int
) -> (User, Iterable[Lesson]):
    sql = select(User, Group).where(
        User.id == user_id, User.group_id == Group.id
    )
    result = await session.execute(sql)
    user_instance: User = result.scalars().first()

    lessons: Iterable[Lesson] = await session.run_sync(
        lambda _: user_instance.Group.lessons
    )

    return user_instance, lessons
