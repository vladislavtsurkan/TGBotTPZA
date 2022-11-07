from aiogram import types
from sqlalchemy import select, delete, update
from aiohttp.client_exceptions import ClientConnectorError
from sqlalchemy.orm import joinedload

from database.models import User, Faculty, Department, Group, Discipline, Lesson, Teacher
from parser.parsing import parse_schedule_tables
from parser.datatypes import LessonTuple
from services.utils import get_or_create


async def add_information_from_schedule_to_db(msg: types.Message, group_instance: Group) -> None:
    db_session = msg.bot.get('db')
    try:
        schedule_lessons_tuple: list[LessonTuple] = await parse_schedule_tables(group_instance.schedule_url)
    except ClientConnectorError:
        return

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


async def create_faculty(msg: types.Message, title: str, title_short: str) -> Faculty:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(Faculty).where(Faculty.title == title)
        faculty_instance, is_created = await get_or_create(
            session, Faculty, sql, title=title, title_short=title_short
        )

    return faculty_instance


async def create_department(msg: types.Message, faculty_id: int, title: str, title_short: str) -> Department:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(Department).where(Department.title == title)
        department_instance, is_created = await get_or_create(
            session, Department, sql, faculty_id=faculty_id, title=title, title_short=title_short
        )

    return department_instance


async def create_group(msg: types.Message, department_id: int, title: str, url_schedule: str) -> Group:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(Group).where(Group.department_id == department_id, Group.title == title)
        group_instance, is_created = await get_or_create(session, Group, sql, department_id=department_id,
                                                         title=title, schedule_url=url_schedule)

    return group_instance


async def get_information_group(msg: types.Message, *, group_id, department_id) -> Group:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql_group_info = select(Group, Department, Faculty).where(
            Group.department_id == Department.id,
            Department.faculty_id == Faculty.id,
            Group.department_id == department_id,
            Group.id == group_id
        ).options(joinedload(Group.Department).subqueryload(Department.Faculty))
        result = await session.execute(sql_group_info)
        group: Group = result.scalars().first()

        return group


async def delete_group(msg: types.Message | types.CallbackQuery, *, group_id: int, department_id: int) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql_group_table = delete(Group).where(Group.department_id == department_id, Group.id == group_id)
        sql_group_lesson_table = f'DELETE FROM lesson_group WHERE group_id = {group_id}'
        sql_user_group = delete(User).where(User.group_id == group_id)

        await session.execute(sql_group_lesson_table)
        await session.execute(sql_group_table)
        await session.execute(sql_user_group)
        await session.commit()


async def change_title_group(msg: types.Message, new_title: str, *, group_id: int, department_id: int) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = update(Group).where(Group.id == group_id, Group.department_id == department_id).values(title=new_title)
        await session.execute(sql)
        await session.commit()


async def change_department_group(msg: types.Message, new_department_id: str, *, group_id: int,
                                  department_id: int) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = update(Group).where(Group.id == group_id, Group.department_id == department_id).\
            values(department_id=new_department_id)
        await session.execute(sql)
        await session.commit()


async def change_url_schedule_group(msg: types.Message, new_url: str, *, group_id) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql_update_url = update(Group).where(Group.id == group_id).values(schedule_url=new_url)
        sql_group_lesson_table = f'DELETE FROM lesson_group WHERE group_id = {group_id}'
        await session.execute(sql_group_lesson_table)
        await session.execute(sql_update_url)
        await session.commit()
        sql_group = select(Group).where(Group.id == group_id)
        result = await session.execute(sql_group)
        group_instance = result.scalars().first()

    await add_information_from_schedule_to_db(msg, group_instance)


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
