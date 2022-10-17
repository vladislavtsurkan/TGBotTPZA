from typing import Any
from aiogram import types, Dispatcher
from sqlalchemy import select
from sqlalchemy.sql.selectable import Select

from database.models import User, Faculty, Department, Group, Discipline, Lesson, Teacher, Task

from parser.parsing import parse_schedule_tables
from parser.datatypes import LessonTuple


async def is_user_admin(msg: types.Message):
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(User).where(User.id == msg.from_user.id)
        result = await session.execute(sql)
        user = result.scalars().first()

        if user is not None:
            return user.is_admin
        else:
            await msg.answer('Ви не зареєстровані в системі.')
            return False


async def get_or_create(session, class_model: Any, sql: Select, **kwargs) -> (Any, bool):
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


async def add_information_from_schedule_to_db(msg: types.Message, group_instance: Group) -> None:
    db_session = msg.bot.get('db')
    schedule_lessons_tuple: list[LessonTuple] = await parse_schedule_tables(group_instance.schedule_url)

    async with db_session() as session:
        for lesson in schedule_lessons_tuple:
            discipline_title, teachers, location, week, day_number, lesson_number = (
                lesson.discipline, lesson.teachers, lesson.location, lesson.week,
                lesson.day_number, lesson.lesson_number
            )
            sql_discipline = select(Discipline).where(Discipline.title == discipline_title)
            discipline_instance, is_created = await get_or_create(session, Discipline, sql_discipline,
                                                                  title=discipline_title)

            sql_lesson = select(Lesson). \
                where(Lesson.discipline_id == discipline_instance.id,
                      Lesson.week == week,
                      Lesson.day == day_number,
                      Lesson.number_lesson == lesson_number)
            lesson_instance, is_created = await get_or_create(session, Lesson, sql_lesson,
                                                              discipline_id=discipline_instance.id,
                                                              type_and_location=location,
                                                              week=week, day=day_number, number_lesson=lesson_number)

            for full_name in teachers:
                sql_teacher = select(Teacher).where(Teacher.full_name == full_name)
                teacher_instance, is_created = await get_or_create(session, Teacher, sql_teacher, full_name=full_name)

                teachers = await session.run_sync(lambda session_sync: lesson_instance.teachers)
                if teacher_instance not in teachers:
                    await session.run_sync(lambda session_sync: lesson_instance.teachers.append(teacher_instance))

            await session.run_sync(lambda session_sync: lesson_instance.groups.append(group_instance))
            await session.commit()


async def create_group(msg: types.Message, department_id: int, title: str, url_schedule: str):
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(Group).where(Group.department_id == department_id, Group.title == title)
        group_instance, is_created = await get_or_create(session, Group, sql, department_id=department_id,
                                                         title=title, schedule_url=url_schedule)

    return group_instance


async def just_def(msg: types.Message):
    db_session = msg.bot.get('db')

    async with db_session() as session:
        s = select(User).where(User.id == 1)
        print(type(s), type(select), type(session))
