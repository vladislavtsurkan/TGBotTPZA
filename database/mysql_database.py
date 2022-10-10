import traceback

from sqlalchemy import create_engine, Column, ForeignKey, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError

engine = create_engine('mysql+mysqlconnector://vlad_mysql:@localhost/schedule_bot_db')

Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    sur_name = Column(String(30), nullable=False)
    group_id = Column(Integer, ForeignKey('Groups.id'))

    is_admin = Column(Boolean, default=False, nullable=False)
    is_leader = Column(Boolean, default=False, nullable=False)

    Group = relationship('Group')


class Faculty(Base):
    __tablename__ = 'Faculties'

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    title_short = Column(String(10))


class Department(Base):
    __tablename__ = 'Departments'

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    title_short = Column(String(10))
    faculty_id = Column(Integer, ForeignKey('Faculties.id'))


class Group(Base):
    __tablename__ = 'Groups'

    id = Column(Integer, primary_key=True)
    title = Column(String(10))
    schedule_url = Column(String(200))
    department_id = Column(Integer, ForeignKey('Departments.id'))


class Discipline(Base):
    __tablename__ = 'Disciplines'

    id = Column(Integer, primary_key=True)
    title = Column(String(150))


class Lesson(Base):
    __tablename__ = 'Lessons'

    id = Column(Integer, primary_key=True)
    discipline_id = Column(Integer, ForeignKey('Disciplines.id'))
    week = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    number_lesson = Column(Integer, nullable=False)
    type_and_location = Column(String(50), nullable=False)

    Discipline = relationship('Discipline')


class Teacher(Base):
    __tablename__ = 'Teachers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    sur_name = Column(String(30), nullable=False)


class Task(Base):
    __tablename__ = 'Tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id'))
    description = Column(String(200), nullable=False)

    User = relationship('User')


def update_database():
    print('The database update process has started.')
    try:
        Base.metadata.create_all(engine)
    except SQLAlchemyError:
        print('SQLAlchemyError! We don`t update database.')
        traceback.print_exc()
    finally:
        print('The database update process has been completed.')
