# from datetime import date
import datetime
import xlparser.parser as parser
from aiogram.utils.markdown import escape_md, text, bold, italic
from loguru import logger

def parse_day(data: list) -> str:
    lessons = []
    header = f'{data[0][2].capitalize()} | '
    flag = True
    for lesson in data:
        # Skip emty lessons
        if lesson[3] == '':
            continue
        lessons.append(f'{lesson[6]}. {lesson[4].upper()} | {lesson[3]} | {lesson[5]}')
        if lesson[5] != 'Д':
            flag = False

    if flag:
        header += 'Дистанционное обучение\n\n'
    else:
        header += 'Очные занятия\n\n'

    res = header + '\n'.join(lessons)
    return res

def craft_schedule(group: str, mode: int) -> str:
    today = date.today()
    data = []
    res = ''
    if mode == 0:
        data = parser.get_TodaySchedule(today, group)
    elif mode == 1:
        data = parser.get_TomorrowSchedule(today, group)
    elif mode == 2:
        data = parser.get_WeekSchedule(today, group)

    if mode == 0 or mode == 1:
        # Parsing today and next similar
        res = parse_day(data)
    elif mode == 2:
        n = len(data)
        # 6 - count of days
        for i in range(n//6):
            res += parse_day(data[i*6:6*(i+1)]) + '\n\n'

    return res