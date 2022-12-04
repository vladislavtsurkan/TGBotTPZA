import pytest

from database.models import Faculty, Department, Group
from services.admin import (
    create_faculty,
    create_department,
    create_group,
    get_faculty_instance_by_title,
    get_department_instance_by_title,
    get_groups_instances_by_title,
    get_group_instance_by_id,
    change_title_for_faculty,
    change_title_for_department,
    change_title_for_group,
    change_url_schedule_for_group,
    change_department_for_group,
    change_faculty_for_department,
    delete_faculty,
    delete_department,
    delete_group,
    is_group_exist_by_title_and_department_id
)

@pytest.mark.asyncio
async def test_create_faculty(get_sessionmaker):
    faculty_instance: Faculty = await create_faculty(
        get_sessionmaker, 'Інженерно-хімічний факультет', 'ІХФ'
    )
    assert faculty_instance.title == 'Інженерно-хімічний факультет'


@pytest.mark.asyncio
async def test_get_faculty_instance_by_title(get_sessionmaker):
    faculty_instance: Faculty = await get_faculty_instance_by_title(
        get_sessionmaker, 'Інженерно-хімічний факультет'
    )
    assert faculty_instance.title == 'Інженерно-хімічний факультет'


@pytest.mark.asyncio
async def test_change_title_for_faculty(get_sessionmaker):
    faculty_instance: Faculty = await get_faculty_instance_by_title(
        get_sessionmaker, 'Інженерно-хімічний факультет'
    )
    await change_title_for_faculty(
        get_sessionmaker, faculty_id=faculty_instance.id, title='test', title_short='test'
    )
    faculty_instance: Faculty = await get_faculty_instance_by_title(
        get_sessionmaker, 'test'
    )
    assert (
            faculty_instance is not None and
            faculty_instance.title == 'test' and
            faculty_instance.title_short == 'test'
    )
    await change_title_for_faculty(
        get_sessionmaker,
        faculty_id=faculty_instance.id,
        title='Інженерно-хімічний факультет',
        title_short='ІХФ'
    )
    faculty_instance: Faculty = await get_faculty_instance_by_title(
        get_sessionmaker, 'Інженерно-хімічний факультет'
    )
    assert (
            faculty_instance is not None and
            faculty_instance.title == 'Інженерно-хімічний факультет' and
            faculty_instance.title_short == 'ІХФ'
    )


@pytest.mark.asyncio
async def test_create_department(get_sessionmaker):
    faculty_instance: Faculty = await get_faculty_instance_by_title(
        get_sessionmaker, 'Інженерно-хімічний факультет'
    )
    department_intance: Department = await create_department(
        get_sessionmaker,
        faculty_instance.id,
        'Технічних та програмних засобів автоматизації',
        'ТПЗА'
    )
    assert department_intance.title == 'Технічних та програмних засобів автоматизації'


@pytest.mark.asyncio
async def test_get_department_instance_by_title(get_sessionmaker):
    department_instance: Department = await get_department_instance_by_title(
        get_sessionmaker, 'Технічних та програмних засобів автоматизації'
    )
    assert department_instance.title == 'Технічних та програмних засобів автоматизації'


@pytest.mark.asyncio
async def test_change_title_for_department(get_sessionmaker):
    department_instance: Department = await get_department_instance_by_title(
        get_sessionmaker, 'Технічних та програмних засобів автоматизації'
    )
    await change_title_for_department(
        get_sessionmaker, department_id=department_instance.id, title='test', title_short='test'
    )
    department_instance: Department = await get_department_instance_by_title(
        get_sessionmaker, 'test'
    )
    assert (
            department_instance is not None and
            department_instance.title == 'test' and
            department_instance.title_short == 'test'
    )
    await change_title_for_department(
        get_sessionmaker,
        department_id=department_instance.id,
        title='Технічних та програмних засобів автоматизації',
        title_short='ТПЗА'
    )
    department_instance: Department = await get_department_instance_by_title(
        get_sessionmaker, 'Технічних та програмних засобів автоматизації'
    )
    assert (
            department_instance is not None and
            department_instance.title == 'Технічних та програмних засобів автоматизації' and
            department_instance.title_short == 'ТПЗА'
    )


@pytest.mark.asyncio
async def test_change_faculty_for_department(get_sessionmaker):
    department_instance: Department = await get_department_instance_by_title(
        get_sessionmaker, 'Технічних та програмних засобів автоматизації'
    )
    faculty_instance: Faculty = await get_faculty_instance_by_title(
        get_sessionmaker, 'Інженерно-хімічний факультет'
    )
    new_faculty_instance = await create_faculty(
        get_sessionmaker, 'Інститут атомної та теплової енергетики', 'ІАТЕ'
    )
    await change_faculty_for_department(
        get_sessionmaker, department_id=department_instance.id, faculty_id=new_faculty_instance.id
    )
    department_instance: Department = await get_department_instance_by_title(
        get_sessionmaker, 'Технічних та програмних засобів автоматизації'
    )
    assert department_instance.faculty_id == new_faculty_instance.id
    await change_faculty_for_department(
        get_sessionmaker, department_id=department_instance.id, faculty_id=faculty_instance.id
    )
    department_instance: Department = await get_department_instance_by_title(
        get_sessionmaker, 'Технічних та програмних засобів автоматизації'
    )
    assert department_instance.faculty_id == faculty_instance.id


@pytest.mark.asyncio
async def test_create_group(get_sessionmaker):
    department_instance: Department = await get_department_instance_by_title(
        get_sessionmaker, 'Технічних та програмних засобів автоматизації'
    )
    group_instance: Group = await create_group(
        get_sessionmaker, department_instance.id, 'ЛА-п11', 'http://epi.kpi.ua'
    )
    assert group_instance.title == 'ЛА-п11'

@pytest.mark.asyncio
async def test_is_group_exist_by_title_and_department_id(get_sessionmaker):
    department_instance: Department = await get_department_instance_by_title(
        get_sessionmaker, 'Технічних та програмних засобів автоматизації'
    )
    is_exist, _ = await is_group_exist_by_title_and_department_id(
        get_sessionmaker, 'ЛА-п11', department_instance.id
    )
    assert is_exist


@pytest.mark.asyncio
async def test_get_groups_instances_by_title(get_sessionmaker):
    group_instances_by_title: list[Group] = await get_groups_instances_by_title(
        get_sessionmaker, 'ЛА-п11'
    )
    assert group_instances_by_title[0].title == 'ЛА-п11'


@pytest.mark.asyncio
async def test_get_group_instance_by_id(get_sessionmaker):
    group_intances: list[Group] = await get_groups_instances_by_title(
        get_sessionmaker, 'ЛА-п11'
    )
    group_instance: Group = group_intances[0]
    group_instance_copy: Group = await get_group_instance_by_id(
        get_sessionmaker, group_id=group_instance.id, department_id=group_instance.department_id
    )
    assert (
        group_instance_copy.title == 'ЛА-п11' and
        group_instance_copy.id == group_instance.id
    )


@pytest.mark.asyncio
async def test_change_title_for_group(get_sessionmaker):
    group_intances: list[Group] = await get_groups_instances_by_title(
        get_sessionmaker, 'ЛА-п11'
    )
    group_intance: Group = group_intances[0]
    await change_title_for_group(
        get_sessionmaker, 'test', group_id=group_intance.id, department_id=group_intance.department_id
    )
    group_instance: Group = await get_group_instance_by_id(
        get_sessionmaker, group_id=group_intance.id, department_id=group_intance.department_id
    )
    assert group_instance.title == 'test'
    await change_title_for_group(
        get_sessionmaker, 'ЛА-п11', group_id=group_instance.id, department_id=group_instance.department_id
    )
    group_instance: Group = await get_group_instance_by_id(
        get_sessionmaker, group_id=group_instance.id, department_id=group_instance.department_id
    )
    assert group_instance.title == 'ЛА-п11'


@pytest.mark.asyncio
async def test_change_department_for_group(get_sessionmaker):
    faculty_instance: Faculty = await get_faculty_instance_by_title(
        get_sessionmaker, 'Інженерно-хімічний факультет'
    )
    department_instance: Department = await get_department_instance_by_title(
        get_sessionmaker, 'Технічних та програмних засобів автоматизації'
    )
    group_intances: list[Group] = await get_groups_instances_by_title(
        get_sessionmaker, 'ЛА-п11'
    )
    group_instance: Group = group_intances[0]
    new_department_intance = await create_department(
        get_sessionmaker, faculty_instance.id, 'Просто тестова кафедра', 'ПТФ'
    )
    await change_department_for_group(
        get_sessionmaker,
        new_department_intance.id,
        department_id=group_instance.department_id,
        group_id=group_instance.id
    )
    group_instance: Group | None = await get_group_instance_by_id(
        get_sessionmaker, group_id=group_instance.id, department_id=new_department_intance.id
    )
    assert group_instance is not None and group_instance.department_id == new_department_intance.id
    await change_department_for_group(
        get_sessionmaker, department_instance.id,
        department_id=new_department_intance.id,
        group_id=group_instance.id
    )
    group_instance: Group = await get_group_instance_by_id(
        get_sessionmaker, group_id=group_instance.id, department_id=department_instance.id
    )
    assert group_instance is not None and group_instance.department_id == department_instance.id


@pytest.mark.asyncio
async def test_change_url_schedule_for_group(get_sessionmaker):
    group_instances: list[Group] = await get_groups_instances_by_title(
        get_sessionmaker, 'ЛА-п11'
    )
    group_instance: Group = group_instances[0]
    old_schedule_url = group_instance.schedule_url
    is_change_url_schedule = await change_url_schedule_for_group(
        get_sessionmaker, 'http://epi.kpi.ua/test', group_id=group_instance.id
    )
    group_instance: Group = await get_group_instance_by_id(
        get_sessionmaker, group_id=group_instance.id, department_id=group_instance.department_id
    )
    assert (
        group_instance.schedule_url == 'http://epi.kpi.ua/test' if is_change_url_schedule else old_schedule_url
    )


@pytest.mark.asyncio
async def test_delete_group(get_sessionmaker):
    group_instances: list[Group] = await get_groups_instances_by_title(
        get_sessionmaker, "ЛА-п11"
    )
    group_instance: Group = group_instances[0]
    await delete_group(
        get_sessionmaker, group_id=group_instance.id, department_id=group_instance.department_id
    )
    group_instances: list[Group] = await get_groups_instances_by_title(
        get_sessionmaker, "ЛА-п11"
    )
    assert not group_instances


@pytest.mark.asyncio
async def test_delete_department(get_sessionmaker):
    department_instance: Department = await get_department_instance_by_title(
        get_sessionmaker, "Технічних та програмних засобів автоматизації"
    )
    await delete_department(
        get_sessionmaker, department_id=department_instance.id
    )
    department_intance: Department = await get_department_instance_by_title(
        get_sessionmaker, "Технічних та програмних засобів автоматизації"
    )
    assert department_intance is None


@pytest.mark.asyncio
async def test_delete_faculty(get_sessionmaker):
    faculty_instance: Faculty = await get_faculty_instance_by_title(
        get_sessionmaker, "Інженерно-хімічний факультет"
    )
    await delete_faculty(
        get_sessionmaker, faculty_instance.id
    )
    faculty_intance: Faculty = await get_faculty_instance_by_title(
        get_sessionmaker, "Інженерно-хімічний факультет"
    )
    assert faculty_intance is None
