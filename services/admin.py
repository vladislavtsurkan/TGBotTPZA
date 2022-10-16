from aiogram import types, Dispatcher
from sqlalchemy import select

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


def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


async def add_information_from_schedule_to_db(msg: types.Message, url_schedule: str, group_id: int) -> None:
    db_session = msg.bot.get('db')
    schedule_lessons_tuple = await parse_schedule_tables(url_schedule)

    async with db_session() as session:
        for lesson in schedule_lessons_tuple:
            discipline_title, teachers, locations, week, day_number, lesson_number = (
                lesson.discipline, lesson.teachers, lesson.locations, lesson.week,
                lesson.day_number, lesson.lesson_number
            )

            teachers_created = []
            for teacher in teachers:
                teacher_created = Teacher(full_name=teacher)
                teachers_created.append(teacher_created)
                await session.merge(teacher_created)

            await session.merge(Lesson())


async def just_def(msg: types.Message):
    db_session = msg.bot.get('db')

    async with db_session() as session:
        print(session.query(Group).filter(Group.title.lower() == "ла-п11".lower()))
