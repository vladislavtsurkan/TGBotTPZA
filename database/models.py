from sqlalchemy import Column, ForeignKey, String, Integer, Boolean, Table
from sqlalchemy.orm import relationship

from database.base import Base


class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('Groups.id'))
    is_admin = Column(Boolean, default=False, nullable=False)

    Group = relationship('Group')

    def __repr__(self):
        return f'<User {self.id}>'


class Faculty(Base):
    __tablename__ = 'Faculties'

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False, unique=True)
    title_short = Column(String(10), nullable=False)

    def __repr__(self):
        return f'<Faculty "{self.title}" ({self.title_short})>'


class Department(Base):
    __tablename__ = 'Departments'

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False, unique=True)
    title_short = Column(String(10), nullable=False)
    faculty_id = Column(Integer, ForeignKey('Faculties.id'))

    Faculty = relationship('Faculty')

    def __repr__(self):
        return f'<Department "{self.title}" ({self.title_short})>'


class Group(Base):
    __tablename__ = 'Groups'

    id = Column(Integer, primary_key=True)
    title = Column(String(10), unique=True)
    schedule_url = Column(String(200))
    department_id = Column(Integer, ForeignKey('Departments.id'))

    Department = relationship('Department')

    def __repr__(self):
        return f'<Group "{self.title}">'


class Discipline(Base):
    __tablename__ = 'Disciplines'

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False, unique=True)

    def __repr__(self):
        return f'<Discipline "{self.title}">'


lesson_teacher = Table('lesson_teacher', Base.metadata,
                       Column('teacher_id', Integer, ForeignKey('Teachers.id')),
                       Column('lesson_id', Integer, ForeignKey('Lessons.id')))

lesson_group = Table('lesson_group', Base.metadata,
                     Column('group_id', Integer, ForeignKey('Groups.id')),
                     Column('lesson_id', Integer, ForeignKey('Lessons.id')))


class Lesson(Base):
    __tablename__ = 'Lessons'

    id = Column(Integer, primary_key=True)
    discipline_id = Column(Integer, ForeignKey('Disciplines.id'))
    groups = relationship('Group', secondary=lesson_group, backref='lessons')
    teachers = relationship('Teacher', secondary=lesson_teacher, backref='lessons')
    week = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    number_lesson = Column(Integer, nullable=False)
    type_and_location = Column(String(50), nullable=False)

    Discipline = relationship('Discipline')

    def __repr__(self):
        return f'<Lesson by Discipline "{self.Discipline.title}">'


class Teacher(Base):
    __tablename__ = 'Teachers'

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), unique=True)

    def __repr__(self):
        return f'<Teacher "{self.full_name}">'


class Task(Base):
    __tablename__ = 'Tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id'))
    description = Column(String(200), nullable=False)

    User = relationship('User')

    def __repr__(self):
        return f'<Task by User {self.user_id}>'
