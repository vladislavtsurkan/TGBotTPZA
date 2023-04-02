from loguru import logger

from sqlalchemy import select, update, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from aiohttp.client_exceptions import ClientConnectorError

from database.models import User, Faculty, Department, Group, Discipline, Lesson, Teacher
from parser.parsing import parse_schedule_tables
from parser.datatypes import LessonTuple
from services.utils import get_or_create


async def try_register_first_admin(*, user_id: int, session: AsyncSession) -> bool:
    """Create first admin user in database if not exist admin users"""
    sql = select(User).where(User.is_admin == True)
    result = await session.execute(sql)
    admin_user = result.scalars().first()

    if admin_user is None:
        try:
            await session.merge(User(id=user_id, is_admin=True))
            await session.commit()
        except SQLAlchemyError:
            logger.exception('Failed try register first admin')
            return False
        else:
            return True

    return False


async def add_information_from_schedule_to_db(
        group_instance: Group, *, session: AsyncSession
) -> bool:
    """Added information from schedule to database tables"""
    try:
        schedule_lessons_tuple: list[LessonTuple] = await parse_schedule_tables(
            group_instance.schedule_url
        )
    except ClientConnectorError:
        logger.warning('Failed try get schedule from site')
        return False

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
                lambda _: lesson_instance.teachers
            )
            if teacher_instance not in lesson_teachers:
                await session.run_sync(
                    lambda _: lesson_instance.teachers.append(teacher_instance)
                )

        lesson_groups = await session.run_sync(
            lambda _: lesson_instance.groups
        )
        if group_instance not in lesson_groups:
            await session.run_sync(
                lambda _: lesson_instance.groups.append(group_instance)
            )

    await session.commit()

    return True


async def create_faculty(title: str, title_short: str, *, session: AsyncSession) -> Faculty:
    """Create faculty instance in database"""
    sql = select(Faculty).where(Faculty.title == title)
    faculty_instance, _ = await get_or_create(
        session, Faculty, sql, title=title, title_short=title_short
    )

    return faculty_instance


async def get_faculty_instance_by_title(title: str, *, session: AsyncSession) -> Faculty | None:
    """Get faculty instance by title"""
    sql = select(Faculty).where(Faculty.title == title)
    result = await session.execute(sql)
    faculty_instance: Faculty | None = result.scalars().first()
    return faculty_instance


async def change_title_for_faculty(
        *, faculty_id: int, title: str, title_short: str, session: AsyncSession
) -> None:
    """Change title for faculty in database by faculty_id"""
    sql = update(Faculty).where(
        Faculty.id == faculty_id
    ).values(
        title=title, title_short=title_short
    )
    await session.execute(sql)
    await session.commit()


async def delete_faculty(
        faculty_id: int, *, session: AsyncSession, committing: bool = True
) -> None:
    """Delete faculty instance in database by faculty_id with cascade"""
    sql_select_departments = select(Department).where(
        Department.faculty_id == faculty_id
    )
    result = await session.execute(sql_select_departments)
    departments = result.scalars().all()

    for department in departments:
        await delete_department(department_id=department.id, session=session, committing=False)

    sql = delete(Faculty).where(Faculty.id == faculty_id)
    await session.execute(sql)

    if committing:
        await session.commit()


async def create_department(
        faculty_id: int, title: str, title_short: str, *, session: AsyncSession
) -> Department:
    """Create department instance in database"""
    sql = select(Department).where(Department.title == title)
    department_instance, _ = await get_or_create(
        session, Department, sql, faculty_id=faculty_id, title=title, title_short=title_short
    )
    return department_instance


async def get_department_instance_by_title(
        title: str, *, session: AsyncSession
) -> Department | None:
    """Get department instance by title"""
    sql = select(Department, Faculty).where(
        Department.title == title, Department.faculty_id == Faculty.id
    ).options(joinedload(Department.Faculty))
    result = await session.execute(sql)
    department_instance: Department | None = result.scalars().first()
    return department_instance


async def change_faculty_for_department(
        *, department_id: int, faculty_id: int, session: AsyncSession
) -> None:
    """Change faculty for department in database by department_id"""
    sql = update(Department).where(
        Department.id == department_id
    ).values(
        faculty_id=faculty_id
    )
    await session.execute(sql)
    await session.commit()


async def change_title_for_department(
        *, department_id: int, title: str, title_short: str, session: AsyncSession
) -> None:
    """Change title for department in database by department_id"""
    sql = update(Department).where(
        Department.id == department_id
    ).values(
        title=title, title_short=title_short
    )
    await session.execute(sql)
    await session.commit()


async def delete_department(
        *, department_id: int, session: AsyncSession, committing: bool = True
) -> None:
    """Delete department instance in database by department_id with cascade"""
    sql_select_group = select(Group).where(Group.department_id == department_id)
    result = await session.execute(sql_select_group)
    groups = result.scalars().all()

    for group in groups:
        await delete_group(
            group_id=group.id,
            department_id=department_id,
            session=session,
            committing=False
        )

    sql_delete_department = delete(Department).where(Department.id == department_id)
    await session.execute(sql_delete_department)

    if committing:
        await session.commit()


async def create_group(
        department_id: int, title: str, url_schedule: str, *, session: AsyncSession
) -> Group:
    """Create group instance in database"""
    sql = select(Group).where(Group.department_id == department_id, Group.title == title)
    group_instance, _ = await get_or_create(
        session, Group, sql, department_id=department_id,
        title=title, schedule_url=url_schedule
    )
    return group_instance


async def get_groups_instances_by_title(title: str, *, session: AsyncSession) -> list[Group]:
    """Get groups instances by title"""
    sql_groups = select(Group, Department, Faculty).where(
        Group.department_id == Department.id,
        Department.faculty_id == Faculty.id,
        Group.title == title
    ).options(joinedload(Group.Department).subqueryload(Department.Faculty))
    result = await session.execute(sql_groups)
    return list(result.scalars())


async def is_group_exist_by_title_and_department_id(
        title: str, department_id: int, *, session: AsyncSession
) -> (bool, Group | None):
    """Check group exist in database by title and department_id"""
    sql = select(Group).where(Group.title == title, Group.department_id == department_id)
    result = await session.execute(sql)
    group_instance = result.scalars().first()
    return (is_exist := (group_instance is not None)), group_instance if is_exist else None


async def get_group_instance_by_id(
        *, group_id, department_id, session: AsyncSession
) -> Group | None:
    """Get group instance by id"""
    sql_group_info = select(Group, Department, Faculty).where(
        Group.department_id == Department.id,
        Department.faculty_id == Faculty.id,
        Group.department_id == department_id,
        Group.id == group_id
    ).options(joinedload(Group.Department).subqueryload(Department.Faculty))
    result = await session.execute(sql_group_info)
    group: Group = result.scalars().first()

    return group


async def delete_group(
        *, group_id: int, department_id: int, session: AsyncSession, committing: bool = True
) -> None:
    """Delete group instance in database by group_id"""
    sql_group_table = delete(Group).where(
        Group.department_id == department_id, Group.id == group_id
    )
    sql_group_lesson_table = text('DELETE FROM lesson_group WHERE group_id = :group_id')
    sql_user_group = delete(User).where(User.group_id == group_id)

    await session.execute(sql_group_lesson_table, {'group_id': group_id})
    await session.execute(sql_group_table)
    await session.execute(sql_user_group)

    if committing:
        await session.commit()


async def change_title_for_group(
        new_title: str, *, group_id: int, department_id: int, session: AsyncSession
) -> None:
    """Change title for group in database by group_id and department_id"""
    sql = update(Group).where(
        Group.id == group_id, Group.department_id == department_id
    ).values(
        title=new_title
    )
    await session.execute(sql)
    await session.commit()


async def change_department_for_group(
        new_department_id: int, *, group_id: int, department_id: int, session: AsyncSession
) -> None:
    """Change department for group in database by group_id"""
    sql = update(Group).where(
        Group.id == group_id, Group.department_id == department_id
    ).values(department_id=new_department_id)
    await session.execute(sql)
    await session.commit()


async def change_url_schedule_for_group(
        new_url: str, *, group_id, session: AsyncSession
) -> bool:
    """Change url schedule for group in database by group_id"""
    sql_update_url = update(Group).where(Group.id == group_id).values(schedule_url=new_url)
    sql_group_lesson_table = text('DELETE FROM lesson_group WHERE group_id = :group_id')
    await session.execute(sql_group_lesson_table, {'group_id': group_id})
    await session.execute(sql_update_url)
    await session.commit()
    sql_group = select(Group).where(Group.id == group_id)
    result = await session.execute(sql_group)
    group_instance = result.scalars().first()

    return await add_information_from_schedule_to_db(group_instance, session=session)
