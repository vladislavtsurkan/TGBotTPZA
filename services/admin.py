from sqlalchemy.orm import sessionmaker

from database.mysql_database import engine, User, Teacher, Discipline, Lesson, Group, Task

session = sessionmaker(bind=engine)
s = session()

print(s.query(User).filter(User.is_admin).all())
