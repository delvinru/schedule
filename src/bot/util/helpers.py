from datetime import date

import xlparser.parser as parser
from aiogram import types
from aiogram.utils.markdown import bold, text, escape_md
from loguru import logger


def parse_day(data: list, one_day: bool) -> str:
    lessons = []
    header = f'{data[0][2].capitalize()} | '
    flag = True

    for lesson in data:
        # Skip emty lessons
        if lesson[3] == '':
            continue
        lessons.append(f'{lesson[8]}. {lesson[4].upper()} | {lesson[3]} | {lesson[5]}')
        if lesson[5] != 'Д':
            flag = False

    if flag:
        if one_day:
            header += 'Дистанционное обучение\n\n'
        else:
            header += 'Дистанционное обучение\n'
    else:
        if one_day:
            header += 'Очные занятия\n\n'
        else:
            header += 'Очные занятия\n'

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
        res = parse_day(data, one_day=True)
    elif mode == 2:
        n = len(data)
        # 6 - count of days
        for i in range(n//6):
            res += parse_day(data[i*6:6*(i+1)], one_day=False) + '\n\n'

    return res

def craft_week_message() -> str:
    today = date.today()
    week = parser.get_WeekNumber(today)
    data = text("Текущая неделя: ", bold(str(week)))
    return data

def craft_user_profile(message: types.Message, group: str) -> str:
    data = text(
        "Профиль:\n",
        "Имя пользователя: ",
        bold(message.from_user.username),
        "\nГруппа: ",
        bold(group),
        sep=""
    )
    return data

def craft_time_schedule() -> str:
    # TODO: fix this shit
    group = 'ККСО-01-19'
    today = date.today()
    data = parser.get_WeekSchedule(today, group)
    res = 'Время занятий:\n'
    for i in range(0, 6):
        res += bold(f'{data[i][8]}. ') + escape_md(f'{data[i][6]} : {data[i][7]}\n')
    
    return res
