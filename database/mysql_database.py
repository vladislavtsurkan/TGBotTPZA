from sqlalchemy import Column, ForeignKey, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqlconnector://vlad_mysql:@localhost/la_p11_db')

Base = declarative_base()


class Student(Base):
    __tablename__ = 'Students'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    group_id = Column(Integer, ForeignKey('Groups.id'))
    discipline = relationship('Discipline')

    is_admin = Column(Boolean, default=False, nullable=False)


class Group(Base):
    __tablename__ = 'Groups'

    id = Column(Integer, primary_key=True)
    title = Column(String(10))
    schedule_code = Column(String(200))


class Discipline(Base):
    __tablename__ = 'Disciplines'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    teacher_id = Column(Integer, ForeignKey('Teachers.id'))
    discipline = relationship('Discipline')
    Teacher = relationship('Teacher')


class Teacher(Base):
    __tablename__ = 'Teachers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)


class Task(Base):
    __tablename__ = 'Tasks'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('Students.id'))
    description = Column(String(200), nullable=False)
    Student = relationship('Student')
