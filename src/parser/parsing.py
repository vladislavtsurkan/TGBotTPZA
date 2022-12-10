import asyncio
import aiohttp
from bs4 import BeautifulSoup
from time import time
from pprint import pprint

from src.parser.datatypes import LessonTuple

_unknown_field = "Немає інформації"
_set_days_of_week = {"Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота"}
_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'
}


async def parse_schedule_tables(url: str) -> list[LessonTuple]:
    """Use for parsing schedule tables from http://epi.kpi.ua"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url, allow_redirects=True, headers=_headers) as response:
            data = await response.read()

    soup = BeautifulSoup(data, "lxml")

    tables = soup.find_all("table")

    week_number = 0
    lessons = []

    for table in tables:
        week_number += 1
        trs = table.find_all("tr")
        lesson_number = -1

        for tr in trs:
            lesson_number += 1
            tds = tr.find_all("td")
            day_number = -1

            for td in tds:
                day_number += 1
                if td.find("span", class_="disLabel") is None or td.text.strip() in _set_days_of_week:
                    continue

                tags_a = td.find_all('a', class_='plainLink')
                teachers = []
                disciplines = []
                locations = []

                for tag_a in tags_a:
                    href = tag_a.get('href')

                    if '/Schedules/ViewSchedule.aspx' in href:
                        teachers.append(tag_a.get('title'))
                    elif 'http://maps.google.com' in href:
                        locations.append(tag_a.text)
                    elif 'http://wiki.kpi.ua/' in href:
                        disciplines.append(tag_a.get('title'))

                sort_lessons = _sort_lesson(disciplines, teachers, locations)

                for lesson in sort_lessons:
                    data = LessonTuple(
                        discipline=lesson.get('discipline', _unknown_field),
                        teachers=lesson.get('teacher', []),
                        location=lesson.get('location', _unknown_field),
                        day_number=day_number,
                        week=week_number,
                        lesson_number=lesson_number
                    )
                    lessons.append(data)

    return lessons


def _sort_lesson(disciplines: list[str], teachers: list[str], locations: list[str]
                 ) -> list[dict[str, str]]:
    """Sorting lessons in list of dicts"""
    sort_lessons = []
    sliced_teachers_names = _slice_teachers_names(teachers)

    if len(disciplines) > 1:
        for i, discipline in enumerate(disciplines):
            if not teachers:
                teacher = []
            else:
                try:
                    teacher = [sliced_teachers_names[i]]
                except IndexError:
                    teacher = []

            if not locations:
                location = _unknown_field
            else:
                try:
                    location = locations[i]
                except IndexError:
                    location = _unknown_field

            lesson = {'discipline': discipline, 'location': location, 'teacher': teacher}
            sort_lessons.append(lesson)

    else:
        discipline = disciplines[0]
        teacher = [] if not teachers else sliced_teachers_names
        location = _unknown_field if not locations else ', '.join(locations)

        lesson = {'discipline': discipline, 'location': location, 'teacher': teacher}
        sort_lessons.append(lesson)

    return sort_lessons


def _slice_teachers_names(teachers: list[str]) -> list[str]:
    """Transformed teachers names in string with separator comma"""
    sliced_names = []

    if not teachers:
        return sliced_names

    for teacher in teachers:
        try:
            sliced_names.append(' '. join(teacher.split()[-3:]))
        except IndexError:
            pass

    return sliced_names


async def main():
    time_start = time()
    # ЛА-п11
    lap11 = await parse_schedule_tables(
        'http://epi.kpi.ua/Schedules/ViewSchedule.aspx?g=f761eeb5-f6a2-4019-9d18-6647bd6daa23'
    )
    pprint(lap11)
    print(f'Всього пар: {len(lap11)}')
    # ЛА-91
    la91 = await parse_schedule_tables(
        'http://epi.kpi.ua/Schedules/ViewSchedule.aspx?g=81b68054-0171-4aa6-847e-80a78584638d'
    )
    pprint(la91)
    print(f'Всього пар: {len(la91)}')
    # ЛА-п21
    lap21 = await parse_schedule_tables(
        'http://epi.kpi.ua/Schedules/ViewSchedule.aspx?g=4439a805-5bb5-4e80-8755-fcde49fdf47b'
    )
    pprint(lap21)
    print(f'Всього пар: {len(lap21)}')

    print(f'Пройшло {time() - time_start} секунд')


if __name__ == '__main__':
    asyncio.run(main())
