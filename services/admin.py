from loguru import logger

from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from aiohttp.client_exceptions import ClientConnectorError

from database.models import User, Faculty, Department, Group, Discipline, Lesson, Teacher
from parser.parsing import parse_schedule_tables
from parser.datatypes import LessonTuple
from services.utils import get_or_create


async def add_information_from_schedule_to_db(
        db_session: sessionmaker, group_instance: Group
) -> bool:
    """Added information from schedule to database tables"""
    try:
        schedule_lessons_tuple: list[LessonTuple] = await parse_schedule_tables(
            group_instance.schedule_url
        )
    except ClientConnectorError:
        logger.error('Failed try get schedule from site')
        return False

    async with db_session() as session:
        for lesson in schedule_lessons_tuple:
            discipline_title, teachers, location, week, day_number, lesson_number = (
                lesson.discipline, lesson.teachers, lesson.location, lesson.week,
                lesson.day_number, lesson.lesson_number
            )
            sql_discipline = select(Discipline).where(Discipline.title == discipline_title)
            discipline_instance, _ = await get_or_create(
                session, Discipline, sql_discipline, title=discipline_title
            )

            sql_lesson = select(Lesson). \
                where(Lesson.discipline_id == discipline_instance.id,
                      Lesson.week == week,
                      Lesson.day == day_number,
                      Lesson.number_lesson == lesson_number)
            lesson_instance, _ = await get_or_create(
                session, Lesson, sql_lesson, discipline_id=discipline_instance.id,
                type_and_location=location, week=week,
                day=day_number, number_lesson=lesson_number
            )

            for full_name in teachers:
                sql_teacher = select(Teacher).where(Teacher.full_name == full_name)
                teacher_instance, _ = await get_or_create(
                    session, Teacher, sql_teacher, full_name=full_name
                )

                lesson_teachers = await session.run_sync(
                    lambda session_sync: lesson_instance.teachers
                )
                if teacher_instance not in lesson_teachers:
                    await session.run_sync(
                        lambda session_sync: lesson_instance.teachers.append(teacher_instance)
                    )

            lesson_groups = await session.run_sync(
                lambda session_sync: lesson_instance.groups
            )
            if group_instance not in lesson_groups:
                await session.run_sync(
                    lambda session_sync: lesson_instance.groups.append(group_instance)
                )

        await session.commit()
    return True


async def create_faculty(db_session: sessionmaker, title: str, title_short: str) -> Faculty:
    async with db_session() as session:
        sql = select(Faculty).where(Faculty.title == title)
        faculty_instance, _ = await get_or_create(
            session, Faculty, sql, title=title, title_short=title_short
        )

    return faculty_instance


async def get_faculty_instance_by_title(db_session: sessionmaker, title: str) -> Faculty | None:
    async with db_session() as session:
        sql = select(Faculty).where(Faculty.title == title)
        result = await session.execute(sql)
        faculty_instance: Faculty | None = result.scalars.first()
        return faculty_instance


async def change_title_for_faculty(
        db_session: sessionmaker, *, faculty_id: int, title: str, title_short: str
) -> None:
    async with db_session() as session:
        sql = update(Faculty).where(
            Faculty.id == faculty_id
        ).values(
            title=title, title_short=title_short
        )
        await session.execute(sql)
        await session.commit()


async def delete_faculty(db_session: sessionmaker, faculty_id: int) -> None:
    async with db_session() as session:
        sql_select_departments = select(Department).where(
            Department.faculty_id == faculty_id
        )
        result = await session.execute(sql_select_departments)
        departments = result.scalars.all()

    for department in departments:
        await delete_department(db_session, department_id=department.id)

    async with db_session() as session:
        sql = delete(Faculty).where(Faculty.id == faculty_id)
        await session.execute(sql)
        await session.commit()


async def create_department(
        db_session: sessionmaker, faculty_id: int, title: str, title_short: str
) -> Department:
    async with db_session() as session:
        sql = select(Department).where(Department.title == title)
        department_instance, _ = await get_or_create(
            session, Department, sql, faculty_id=faculty_id, title=title, title_short=title_short
        )

    return department_instance


async def get_department_instance_by_title(
        db_session: sessionmaker, title: str
) -> Department | None:
    async with db_session() as session:
        sql = select(Department, Faculty).where(
            Department.title == title, Department.faculty_id == Faculty.id
        )
        result = await session.execute(sql)
        department_instance: Department | None = result.scalars.first()
        return department_instance


async def change_faculty_for_department(
        db_session: sessionmaker, *, department_id: int, faculty_id: int
) -> None:
    async with db_session() as session:
        sql = update(Department).where(
            Department.id == department_id
        ).values(
            faculty_id=faculty_id
        )
        await session.execute(sql)
        await session.commit()


async def change_title_for_department(
        db_session: sessionmaker, *, department_id: int, title: str, title_short: str
) -> None:
    async with db_session() as session:
        sql = update(Department).where(
            Department.id == department_id
        ).values(
            title=title, title_short=title_short
        )
        await session.execute(sql)
        await session.commit()


async def delete_department(db_session: sessionmaker, *, department_id: int) -> None:
    async with db_session() as session:
        sql_select_group = select(Group).where(Group.department_id == department_id)
        result = await session.execute(sql_select_group)
        groups = result.scalars().all()

    for group in groups:
        await delete_group(db_session, group_id=group.id, department_id=department_id)

    async with db_session() as session:
        sql_delete_department = delete(Department).where(Department.id == department_id)
        await session.execute(sql_delete_department)
        await session.commit()


async def create_group(
        db_session: sessionmaker, department_id: int, title: str, url_schedule: str
) -> Group:
    async with db_session() as session:
        sql = select(Group).where(Group.department_id == department_id, Group.title == title)
        group_instance, _ = await get_or_create(
            session, Group, sql, department_id=department_id,
            title=title, schedule_url=url_schedule
        )

    return group_instance


async def get_groups_by_title(db_session: sessionmaker, title: str) -> list[Group]:
    async with db_session() as session:
        sql_groups = select(Group, Department, Faculty).where(
            Group.department_id == Department.id,
            Department.faculty_id == Faculty.id,
            Group.title == title
        ).options(joinedload(Group.Department).subqueryload(Department.Faculty))
        result = await session.execute(sql_groups)
        return list(result.scalars())


async def is_group_exist_by_title_and_department_id(
        db_session: sessionmaker, title: str, department_id: int
) -> (bool, Group | None):
    async with db_session() as session:
        sql = select(Group).where(Group.title == title, Group.department_id == department_id)
        result = await session.execute(sql)
        group_instance = result.scalars().first()
        return (is_exist := (group_instance is not None)), group_instance if is_exist else None


async def get_group_instance_by_id(db_session: sessionmaker, *, group_id, department_id) -> Group:
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


async def delete_group(db_session: sessionmaker, *, group_id: int, department_id: int) -> None:
    async with db_session() as session:
        sql_group_table = delete(Group).where(
            Group.department_id == department_id, Group.id == group_id
        )
        sql_group_lesson_table = f'DELETE FROM lesson_group WHERE group_id = {group_id}'
        sql_user_group = delete(User).where(User.group_id == group_id)

        await session.execute(sql_group_lesson_table)
        await session.execute(sql_group_table)
        await session.execute(sql_user_group)
        await session.commit()


async def change_title_group(
        db_session: sessionmaker, new_title: str, *, group_id: int, department_id: int
) -> None:
    async with db_session() as session:
        sql = update(Group).where(
            Group.id == group_id, Group.department_id == department_id
        ).values(
            title=new_title
        )
        await session.execute(sql)
        await session.commit()


async def change_department_for_group(
        db_session: sessionmaker, new_department_id: str, *, group_id: int, department_id: int
) -> None:
    async with db_session() as session:
        sql = update(Group).where(Group.id == group_id, Group.department_id == department_id). \
            values(department_id=new_department_id)
        await session.execute(sql)
        await session.commit()


async def change_url_schedule_group(db_session: sessionmaker, new_url: str, *, group_id) -> bool:
    async with db_session() as session:
        sql_update_url = update(Group).where(Group.id == group_id).values(schedule_url=new_url)
        sql_group_lesson_table = f'DELETE FROM lesson_group WHERE group_id = {group_id}'
        await session.execute(sql_group_lesson_table)
        await session.execute(sql_update_url)
        await session.commit()
        sql_group = select(Group).where(Group.id == group_id)
        result = await session.execute(sql_group)
        group_instance = result.scalars().first()

    return await add_information_from_schedule_to_db(db_session, group_instance)


async def register_user(db_session: sessionmaker, group_id: int, *, user_id: int) -> bool:
    async with db_session() as session:
        try:
            await session.merge(
                User(id=user_id, group_id=group_id, is_admin=False)
            )
            await session.commit()
        except SQLAlchemyError:
            logger.error('Failed try save new User in database')
            return False
        else:
            return True
