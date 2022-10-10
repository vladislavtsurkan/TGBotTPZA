from typing import NamedTuple


class LessonTuple(NamedTuple):
    discipline: str
    teachers: list[str]
    locations: list[str]
    week: int
    day_number: int
    lesson_number: int
