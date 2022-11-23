from loguru import logger

from aiogram import types
from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from aiohttp.client_exceptions import ClientConnectorError

from database.models import User, Faculty, Department, Group, Discipline, Lesson, Teacher
from parser.parsing import parse_schedule_tables
from parser.datatypes import LessonTuple
from services.utils import get_or_create


async def add_information_from_schedule_to_db(msg: types.Message, group_instance: Group) -> bool:
    """Added information from schedule to database tables"""
    db_session = msg.bot.get('db')
    try:
        schedule_lessons_tuple: list[LessonTuple] = await parse_schedule_tables(group_instance.schedule_url)
    except ClientConnectorError:
        logger.warning('Failed try get schedule from site')
        return False

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

            lesson_groups = await session.run_sync(lambda session_sync: lesson_instance.groups)
            if group_instance not in lesson_groups:
                await session.run_sync(lambda session_sync: lesson_instance.groups.append(group_instance))

        await session.commit()
    return True


async def create_faculty(msg: types.Message, title: str, title_short: str) -> Faculty:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(Faculty).where(Faculty.title == title)
        faculty_instance, is_created = await get_or_create(
            session, Faculty, sql, title=title, title_short=title_short
        )

    return faculty_instance


async def get_faculty_instance_by_title(msg: types.Message, title: str) -> Faculty | None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(Faculty).where(Faculty.title == title)
        result = await session.execute(sql)
        faculty_instance: Faculty | None = result.scalars.first()
        return faculty_instance


async def change_title_for_faculty(msg: types.Message, *, faculty_id: int, title: str, title_short: str) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = update(Faculty).where(Faculty.id == faculty_id).values(title=title, title_short=title_short)
        await session.execute(sql)
        await session.commit()


async def delete_faculty(msg: types.Message | types.CallbackQuery, faculty_id: int) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql_select_departments = select(Department).where(Department.faculty_id == faculty_id)
        result = await session.execute(sql_select_departments)
        departments = result.scalars.all()

    for department in departments:
        await delete_department(msg, department_id=department.id)

    async with db_session() as session:
        sql = delete(Faculty).where(Faculty.id == faculty_id)
        await session.execute(sql)
        await session.commit()


async def create_department(msg: types.Message, faculty_id: int, title: str, title_short: str) -> Department:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(Department).where(Department.title == title)
        department_instance, is_created = await get_or_create(
            session, Department, sql, faculty_id=faculty_id, title=title, title_short=title_short
        )

    return department_instance


async def get_department_instance_by_title(msg: types.Message, title: str) -> Department | None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(Department, Faculty).where(Department.title == title, Department.faculty_id == Faculty.id)
        result = await session.execute(sql)
        department_instance: Department | None = result.scalars.first()
        return department_instance


async def change_faculty_for_department(msg: types.Message, *, department_id: int, faculty_id: int) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = update(Department).where(Department.id == department_id).values(faculty_id=faculty_id)
        await session.execute(sql)
        await session.commit()


async def change_title_for_department(msg: types.Message, *, department_id: int, title: str,
                                      title_short: str) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = update(Department).where(Department.id == department_id).values(title=title, title_short=title_short)
        await session.execute(sql)
        await session.commit()


async def delete_department(msg: types.Message | types.CallbackQuery, *, department_id: int) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql_select_group = select(Group).where(Group.department_id == department_id)
        result = await session.execute(sql_select_group)
        groups = result.scalars().all()

    for group in groups:
        await delete_group(msg, group_id=group.id, department_id=department_id)

    async with db_session() as session:
        sql_delete_department = delete(Department).where(Department.id == department_id)
        await session.execute(sql_delete_department)
        await session.commit()


async def create_group(msg: types.Message, department_id: int, title: str, url_schedule: str) -> Group:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(Group).where(Group.department_id == department_id, Group.title == title)
        group_instance, is_created = await get_or_create(session, Group, sql, department_id=department_id,
                                                         title=title, schedule_url=url_schedule)

    return group_instance


async def get_groups_by_title(msg: types.Message, title: str) -> list[Group]:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql_groups = select(Group, Department, Faculty).where(
            Group.department_id == Department.id,
            Department.faculty_id == Faculty.id,
            Group.title == title
        ).options(joinedload(Group.Department).subqueryload(Department.Faculty))
        result = await session.execute(sql_groups)
        return list(result.scalars())


async def is_group_exist_by_title_and_department_id(msg: types.Message, title: str, department_id: int) -> \
        (bool, Group | None):
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = select(Group).where(Group.title == title, Group.department_id == department_id)
        result = await session.execute(sql)
        group_instance = result.scalars().first()
        return (is_exist := (group_instance is not None)), group_instance if is_exist else None


async def get_group_instance_by_id(msg: types.Message, *, group_id, department_id) -> Group:
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


async def change_department_for_group(msg: types.Message, new_department_id: str, *, group_id: int,
                                      department_id: int) -> None:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        sql = update(Group).where(Group.id == group_id, Group.department_id == department_id). \
            values(department_id=new_department_id)
        await session.execute(sql)
        await session.commit()


async def change_url_schedule_group(msg: types.Message, new_url: str, *, group_id) -> bool:
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

    return await add_information_from_schedule_to_db(msg, group_instance)


async def register_user(msg: types.Message | types.CallbackQuery, group_id: int) -> bool:
    db_session = msg.bot.get('db')

    async with db_session() as session:
        try:
            await session.merge(
                User(id=msg.from_user.id, group_id=group_id, is_admin=False)
            )
            await session.commit()
        except SQLAlchemyError:
            logger.error('Failed try save new User in database')
            return False
        else:
            return True
