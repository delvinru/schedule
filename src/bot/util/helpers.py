from datetime import date
import datetime

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

    empty_day = not any([lesson[3] for lesson in data])

    if flag and not empty_day:
        if one_day:
            header += 'Дистанционное обучение\n\n'
        else:
            header += 'Дистанционное обучение\n'
    elif not flag and not empty_day:
        if one_day:
            header += 'Очные занятия\n\n'
        else:
            header += 'Очные занятия\n'
    elif empty_day:
        if one_day:
            header += 'День самостоятельных занятий\n\n'
        else:
            header += 'День самостоятельных занятий\n'

    res = header + '\n'.join(lessons)
    return res

def craft_schedule(group: str, mode: int, special_date = None) -> str:
    """
    Craft schedule for user

    group:str - user group

    mode: int: 
    
        0 - today, 1 - tomorrow, 2 - week
    """

    today = date.today()

    if special_date:
        today = special_date

    data = []
    res = ''
    if mode == 0:
        # Check if schedule was requested in sunday, then return next monday
        if today.weekday() == 6:
            today += datetime.timedelta(days=1)
        data = parser.get_TodaySchedule(today, group)
    elif mode == 1:
        # Catch if schedule requested in saturday
        if today.weekday() == 5:
            today += datetime.timedelta(days=1)
        data = parser.get_TomorrowSchedule(today, group)
        # Fix for week number
        today += datetime.timedelta(days=1)
    elif mode == 2:
        data = parser.get_WeekSchedule(today, group)

    if mode == 0 or mode == 1:
        # Parsing today and next similar
        try:
            res = parse_day(data, one_day=True)
        except:
            return 'Возникла ошибочка в получении расписания!'
    elif mode == 2:
        # Parsing week schedule
        day = []
        day_id = data[0][2]
        for lesson in data:
            if day_id == lesson[2]:
                day.append(lesson)
            else:
                res += parse_day(day, one_day=False) + '\n\n'
                day = []
                day_id = lesson[2]
                day.append(lesson)
    res = 'Текущая неделя: ' + str(parser.get_WeekNumber(today)) + '\n' + res
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

def craft_time_schedule(group: str) -> str:
    today = date.today()

    # If sunday, function get_timeSchedule return None
    if today.weekday() == 6:
        today += datetime.timedelta(days=1)

    data = parser.get_TimeSchedule(today, group)

    res = bold('Время занятий:\n', sep="")
    for i, el in enumerate(data):
        res += text(f'{bold(str(i+1))}\. {escape_md(el[0]):>5}: {escape_md(el[1])}\n')
    
    return res
