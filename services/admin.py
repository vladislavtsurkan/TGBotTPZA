from aiogram import types
from sqlalchemy import select

from database.models import User, Faculty, Department, Group, Discipline, Lesson, Teacher, Task
from parser.parsing import parse_schedule_tables
from parser.datatypes import LessonTuple
from services.utils import get_or_create


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

                lesson_teachers = await session.run_sync(lambda session_sync: lesson_instance.teachers)
                if teacher_instance not in lesson_teachers:
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


async def just_def(msg: types.Message) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        s = select(User).where(User.id == 1)
        print(type(s), type(select), type(session))
