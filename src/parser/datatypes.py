from typing import NamedTuple


class LessonTuple(NamedTuple):
    discipline: str
    teachers: list[str]
    location: str
    week: int
    day_number: int
    lesson_number: int
