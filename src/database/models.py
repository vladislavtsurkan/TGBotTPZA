from sqlalchemy import Column, ForeignKey, String, Integer, Boolean, Table, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped

from database.base import Base


class User(Base):
    __tablename__ = 'bot_users'

    id: Mapped[int] = Column(Integer, primary_key=True)
    group_id: Mapped[int] = Column(Integer, ForeignKey('bot_groups.id'))
    is_admin: Mapped[bool] = Column(Boolean, default=False, nullable=False)

    Group = relationship('Group')

    def __repr__(self):
        return f'<User {self.id}>'


class Faculty(Base):
    __tablename__ = 'bot_faculties'

    id: Mapped[int] = Column(Integer, primary_key=True)
    title: Mapped[str] = Column(String(100), nullable=False, unique=True)
    title_short: Mapped[str] = Column(String(10), nullable=False)

    def __repr__(self):
        return f'<Faculty "{self.title}" ({self.title_short})>'


class Department(Base):
    __tablename__ = 'bot_departments'

    id: Mapped[int] = Column(Integer, primary_key=True)
    title: Mapped[str] = Column(String(100), nullable=False, unique=True)
    title_short: Mapped[str] = Column(String(10), nullable=False)
    faculty_id: Mapped[int] = Column(Integer, ForeignKey('bot_faculties.id'))

    Faculty = relationship('Faculty')

    def __repr__(self):
        return f'<Department "{self.title}" ({self.title_short})>'


class Group(Base):
    __tablename__ = 'bot_groups'

    id: Mapped[int] = Column(Integer, primary_key=True)
    title: Mapped[str] = Column(String(10))
    schedule_url: Mapped[str] = Column(String(200))
    department_id: Mapped[int] = Column(Integer, ForeignKey('bot_departments.id'))
    __table_args__ = (
        UniqueConstraint('department_id', 'title', name='_department_id_title_str_uc'),
    )

    Department = relationship('Department')

    def __repr__(self):
        return f'<Group #{self.id} "{self.title}">'


class Discipline(Base):
    __tablename__ = 'bot_disciplines'

    id: Mapped[int] = Column(Integer, primary_key=True)
    title: Mapped[str] = Column(String(200), nullable=False, unique=True)

    def __repr__(self):
        return f'<Discipline "{self.title}">'


lesson_teacher = Table('lesson_teacher', Base.metadata,
                       Column('lesson_id', Integer, ForeignKey('bot_lessons.id')),
                       Column('teacher_id', Integer, ForeignKey('bot_teachers.id')))

lesson_group = Table('lesson_group', Base.metadata,
                     Column('lesson_id', Integer, ForeignKey('bot_lessons.id')),
                     Column('group_id', Integer, ForeignKey('bot_groups.id')))


class Lesson(Base):
    __tablename__ = 'bot_lessons'

    id: Mapped[int] = Column(Integer, primary_key=True)
    discipline_id: Mapped[int] = Column(Integer, ForeignKey('bot_disciplines.id'))
    groups = relationship('Group', secondary=lesson_group, backref='lessons')
    teachers = relationship('Teacher', secondary=lesson_teacher, backref='lessons')
    week: Mapped[int] = Column(Integer, nullable=False)
    day: Mapped[int] = Column(Integer, nullable=False)
    number_lesson: Mapped[int] = Column(Integer, nullable=False)
    type_and_location: Mapped[str] = Column(String(150), nullable=False)

    Discipline = relationship('Discipline')

    def __repr__(self):
        return f'<Lesson #{self.id} by Discipline "{self.Discipline.title}">'


class Teacher(Base):
    __tablename__ = 'bot_teachers'

    id: Mapped[int] = Column(Integer, primary_key=True)
    full_name: Mapped[str] = Column(String(150), unique=True)

    def __repr__(self):
        return f'<Teacher "{self.full_name}">'


class Task(Base):
    __tablename__ = 'bot_tasks'

    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey('bot_users.id'))
    description: Mapped[str] = Column(String(300), nullable=False)

    User = relationship('User')

    def __repr__(self):
        return f'<Task #{self.id} by User {self.user_id}>'
