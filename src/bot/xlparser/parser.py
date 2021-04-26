import json
import os
import re
from datetime import *

import requests
import xlrd
from loguru import logger
from util.settings import db as tm

import xlparser.settings.config as cfg

_ident = 0

def update_MireaSchedule():
    '''
    Обновить всю базу расписания МИРЭА (перед обновлением стирает всю базу до нуля). Генерирует xlsx, json файлы, а также создает
    links.txt - список всех ссылок с сайта. Функция очень время затратная, поэтому лучше включать её только вручную, когда это необходимо. \n
    Функция сначала обрабатывает все файлы, и только после окончания работы загружает их в базу.  
    '''

    get_links(cfg.link_MireaShedule, cfg.links_file)
    get_xlfiles(cfg.links_file)

    # full_groups_shedule = {}
    
    tm.clear_Schedule() # Сначала подключаемся и скачиваем файлы, а только потом удаляем базу

    for filename in os.listdir("./xlparser/xl"):
        # * Полный список групп с расписанием * #
        groups_schedule = parse_xlfiles(filename, cfg.block_tags, cfg.special_tags, cfg.substitute_lessons)
        if groups_schedule == None:
            continue

        # * Записываем расписание в джсон * #
        # convert_in_json(groups_shedule, filename[:-5] + ".json")
        convert_in_postgres(groups_schedule)

        print("filename=" + filename, "Complete!", sep=" ")

        # full_groups_shedule = {**groups_shedule, **full_groups_shedule}                   # Можно сохранять полную базу, которую можно слить в один ОГРОМНЫЙ файл
        groups_schedule.clear() 


    # with open("./json/AllInOne.json", "w", encoding="utf-8") as f:                        # Создание одной большой базы
    #     json.dump(full_groups_shedule, f, sort_keys=True, indent=4, ensure_ascii=False)
    
    tm.single_commit()
    logger.info("Database updated succefully!")

def get_TodaySchedule(today, group):
    '''
    Возвращает расписание [список] группы на сегодня. Возвращает None, если вызов произошел в воскресенье.
    '''
    week_number = get_WeekNumber(today)
    if week_number > 17:
        week_number = 17

    cur = get_TodayList(today, group)
    if cur == None:
        return None

    result = []
    for answer in cur:
        weeks_av = answer[10]
        if week_number in weeks_av:
            result.append(answer)

    return result

def get_TomorrowSchedule(today, group):
    '''
    Возвращает расписание [список] группы на сегодня. Возвращает None, если вызов произошел в cубботу.
    '''
    td = date(today.year, today.month, today.day + 1)
    return get_TodaySchedule(td, group)

def get_WeekSchedule(today, group):
    '''
    Возвращает расписание [список] группы на текущую неделю.
    '''
    week_number = get_WeekNumber(today)
    if week_number > 17:
        week_number = 17
    
    cur = get_WeekList(today, group)
    if cur == None:
        return None

    result = []
    for answer in cur:
        weeks_av = answer[10]
        if week_number in weeks_av:
            result.append(answer)

    return result

def get_NextweekSchedule(today, group):
    '''
    Возвращает расписание [список] группы на следующую неделю.
    '''
    td = date(today.year, today.month, today.day + 7)
    return get_WeekSchedule(td, group)

def get_WeekNumber(today):
    '''
    Возвращает номер недели.
    '''
    ZeroDay = date(cfg.semestr_start[0], cfg.semestr_start[1], cfg.semestr_start[2])
    delta_day = abs((today - ZeroDay).days)
    return delta_day // 7 + 1

def get_TodayList(today, group):
    week_number = get_WeekNumber(today)
    if week_number > 17:
        week_number = 17
    even_week = _get_even_week(week_number)
    week_day = _get_week_day(today.weekday())
    if week_day == "ВОСКРЕСЕНЬЕ":
        return None
    
    cur = tm.select_group_and_week_day(group, week_day, even_week)
    # result = []
    # for answer in cur:
    #     result.append(answer)
    return cur

def get_WeekList(today, group):
    week_number = get_WeekNumber(today)
    if week_number > 17:
        week_number = 17
    even_week = _get_even_week(week_number)
    
    cur = tm.select_group_and_even_week(group, even_week)
    # result = []
    # for answer in cur:
        # result.append(answer)
    return cur

def get_TimeSchedule(today, group):
    '''
    Возвращает список пар времени начала/конца занятий
    '''
    # time_sch = []
    # cur = get_TodayList(today, group)

    # for each in cur:
    #     time_sch.append((each[6], each[7]))
    return time_schedule

def check_GroupExist(group):
    '''
    Проверяет существование группы в базе
    '''

    cur = tm.select_group(group)

    if len(cur) == 0:
        return False
    else:
        return True










# ---- Ниже будет сложно ---- #

def _check_tags(tags, line):
    '''
    Поиск в строке одного из списка тегов. В случае нахождения тега, возвращает строку с этим тегом,
    и None в противном случае. Возвращает первый найденый тег.
    '''
    for i in tags.keys():
        if re.search(i, line) != None:
            return tags[i]
    return None

def _get_week_day(day_number):
    if day_number == 0:
        return "ПОНЕДЕЛЬНИК"
    elif day_number == 1:
        return "ВТОРНИК"
    elif day_number == 2:
        return "СРЕДА"
    elif day_number == 3:
        return "ЧЕТВЕРГ"
    elif day_number == 4:
        return "ПЯТНИЦА"
    elif day_number == 5:
        return "СУББОТА"
    elif day_number == 6:
        return "ВОСКРЕСЕНЬЕ"

def _get_even_week(week_number):
    if week_number % 2 == 0:
        return "EVEN"
    else:
        return "ODD"

def get_links(link, filename="./xlparser/links.txt"):
    '''
    Достает с html-страницы все ссылки формата " http:\/\/ ... .xlsx "
    и записывает в файл links.txt.
    '''
    with open(filename, "w", encoding='utf-8') as f:
        res = requests.get(link)
        print("LINK=" + link, "CODE="+ str(res.status_code), sep=" ")
        if res.status_code == 404:
            print("Something went wrong!")
        else:
            find = re.findall(r"(https:\/\/.*\/(.*.xlsx))", res.text)
            for link in find:
                f.write(link[0] + "\n")

def get_xlfiles(filename="./xlparser/links.txt"):
    '''
    Достает все ссылки из файла links.txt, создаем xl-таблицы, складываем их в папку.
    '''
    try:    
        os.makedirs("xl")
    except:
        pass

    with open("links.txt", "r", encoding="utf-8") as f:
        for link in f.readlines():
            filename = re.findall(r".*\/(.*.xlsx)", link)

            link = link.strip()
            res = requests.get(link)
            print("LINK=" + link, "CODE="+ str(res.status_code), sep=" ")
            if res.status_code == 404:
                print("Something went wrong!")
            else:
                with open("./xl/" + filename[0], "wb") as f:
                    f.write(res.content)

def parse_xlfiles(xlfilename, block_tags=[], special_tags=[], substitute_lessons=[]):
    '''
    Вытаскивает из xl-таблиц все группы и их расписание. Возвращает словарь dic[group]= [[Monday], [Tuesday], [Wednesday]...];\n
    Возвращает None если имя файла имеет block_tags. Также имеет обработчики для special_tags. Если special_tag не найден, 
    то используется стандартный обработчик.
    '''



    # --- Утильные функции --- #

    def _antidot(line, mod=1): # Отчистка от плохих символов
        try:
            if mod == 0:
                line = re.sub(r"\n", " ", line)
                line = re.sub(r" {2,}", " ", line) # Удаление первого вхождение пробелов
            line = line.rstrip() # Удаление последнего вхождения пробелов
            line = re.sub(r"\t", "", line)
            line = re.sub(r"\…+.*", "", line)
        except:
            pass
        return line

    def _substitute(line): # Замена длинных обозначений на короткие
        nonlocal substitute_lessons
        for i in substitute_lessons:
            line = re.sub(i, substitute_lessons[i], line)
        return line

    def _weekslicer(day_lessons): # Обработчик влючения/исключения недель
        lesson, typ, audit, start_time, end_time, order, even, week = day_lessons
        if lesson == "":
            return day_lessons
        arr = []
        find = re.match(r"кр\.? ([\d\, ]+)[нeд]{0,3}\.?", lesson) # кр. 12,15 н. 
        if find != None:
            try:
                find = re.findall(r"\d{1,2}", find.group(1))
                for each in find:
                    week.remove(int(each))
            except:
                pass
            finally:
                return (lesson, typ, audit, start_time, end_time, order, even, week)

        find = re.match(r"([\d\, \-\/н(лк)(пр)]+)[нeд]{1,3}\.?", lesson) # 12,15 н.
        if find != None:
            try:
                f = re.findall(r"(\d{1,2})[ ]*\-[ ]*(\d{1,2})", find.group(1))
                for pair in f:
                    for i in range(int(pair[0]), int(pair[1]) + 1):
                        arr.append(i)
            except:
                pass
            try:
                f = re.findall(r"\d{1,2}", find.group(1))
                for each in f:
                    if int(each) not in arr:
                        arr.append(int(each))
            except:
                pass
            finally:
                week = arr
                week.sort()
                return (lesson, typ, audit, start_time, end_time, order, even, week)
        
        find = re.search(r"\(([\d\, \-\/н]+) [нед]{0,3}\.?\)", lesson) # (12,15 н.)
        if find != None:
            try:
                f = re.findall(r"(\d{1,2})[ ]*-[ ]*(\d{1,2})", find.group(1))
                for pair in f:
                    for i in range(int(pair[0]), int(pair[1]) + 1):
                        arr.append(i)
            except:
                pass
            try:
                f = re.findall(r"\d{1,2}", find.group(1))
                for each in f:
                    if int(each) not in arr:
                        arr.append(int(each))
            except:
                pass
            finally:
                week = arr
                week.sort()
                return (lesson, typ, audit, start_time, end_time, order, even, week)

        find = re.search(r"\(кр. ([\d\, ]+)[нед]{0,3}\.?\)", lesson) # (кр. 12,15 н.) 
        if find != None:
            try:
                find = re.findall(r"\d{1,2}", find.group(1))
                for each in find:
                    week.remove(int(each))
            except:
                pass
            finally:
                return (lesson, typ, audit, start_time, end_time, order, even, week)
        return day_lessons # Ничего не нашли

    def _recurparser(line):
        try:
            line = line.rstrip()
            find = re.search(r"(.*)( {4,}|\n)(.*)", line)
        except:
            find = None
        result = []

        if find == None:
            result.append(_antidot(line, 0))
            return result
        else:
            result.append(_antidot(find.group(1), 0))
            result.extend(_recurparser(find.group(3)))
            return result

    def _twiceschedule(obj): # Обрабочкик двойных объектов на одном слоте
        new_objs = []
        
        lesson = obj[0]
        typ = obj[1]
        audit = obj[2]

        lesson_arr = _recurparser(lesson)

        if len(lesson_arr) == 1:
            obj[2] = _antidot(obj[2], 0)
            new_objs.append(obj)
        else:
            typ_arr = _recurparser(typ)
            audit_arr = _recurparser(audit)
            for i in range(len(lesson_arr)):
                lesson = lesson_arr[i]
                try:
                    typ = typ_arr[i]
                except:
                    typ = typ_arr[len(typ_arr) - 1]
                
                try:
                    audit = audit_arr[i]
                except:
                    audit = audit_arr[len(audit_arr) - 1]

                new_objs.append((lesson, typ, audit, obj[3], obj[4], obj[5], obj[6], obj[7]))
        return new_objs

    def _default_handler(): # Стандартный обработчик 
        nonlocal sheet, groups_schedule, find, col, time_schedule
        for k in range(6): 
            day_lesson = sheet.col_values(col - 1, start_rowx=3 + 12 * k, end_rowx=15 + 12 * k) # Делаем срез предметов
            type_lesson = sheet.col_values(col, start_rowx=3 + 12 * k, end_rowx=15 + 12 * k) # Делаем срез типа заняний (пр, лекция, лаб)
            audit_lesson = sheet.col_values(col + 2, start_rowx=3 + 12 * k, end_rowx=15 + 12 * k) # Делаем срез аудиторий

            for i in range(len(day_lesson)): # Убираем плохие символы 
                day_lesson[i] = _antidot(day_lesson[i], 1)
                day_lesson[i] = _substitute(day_lesson[i])
                type_lesson[i] = _antidot(type_lesson[i])
                audit_lesson[i] = _antidot(audit_lesson[i])
            
            evenodd = 1
            order = 1
            week = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            schedule = []
            time_iter = iter(time_schedule)
            for i in range(len(day_lesson)):
                lesson = day_lesson[i]
                typ = type_lesson[i]
                audit = audit_lesson[i]
                time = next(time_iter)
                if evenodd % 2 == 0:
                    eo = "EVEN"
                else:
                    eo = "ODD"
                obj = [lesson, typ, audit, time[0], time[1], int(order), eo, week.copy()] # Объединяем все в один кортеж
                
                obj_arr = _twiceschedule(obj)
                for i in range(len(obj_arr)):
                    obj_arr[i] = _weekslicer(obj_arr[i])

                schedule.extend(obj_arr) 
                evenodd += 1
                order += 0.5
            
            groups_schedule[find.group(1)][k] = schedule

    def _mag_handler(): # Обработчик магистров
        nonlocal sheet, groups_schedule, find, col, time_schedule
        for k in range(5): 
            day_lesson = sheet.col_values(col - 1, start_rowx=3 + 18 * k, end_rowx=21 + 18 * k) # Делаем срез предметов
            type_lesson = sheet.col_values(col, start_rowx=3 + 18 * k, end_rowx=21 + 18 * k) # Делаем срез типа заняний (пр, лекция, лаб)
            audit_lesson = sheet.col_values(col + 2, start_rowx=3 + 18 * k, end_rowx=21 + 18 * k) # Делаем срез аудиторий

            for i in range(len(day_lesson)):# Убираем плхие символы и т.д.
                day_lesson[i] = _antidot(day_lesson[i], 1)
                day_lesson[i] = _substitute(day_lesson[i])
                type_lesson[i] = _antidot(type_lesson[i])
                audit_lesson[i] = _antidot(audit_lesson[i])
            
            evenodd = 1
            order = 1
            week = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            schedule = []
            time_iter = iter(time_schedule)
            for i in range(len(day_lesson)):
                lesson = day_lesson[i]
                typ = type_lesson[i]
                audit = audit_lesson[i]
                time = next(time_iter)
                if evenodd % 2 == 0:
                    eo = "EVEN"
                else:
                    eo = "ODD"
                obj = [lesson, typ, audit, time[0], time[1], int(order), eo, week.copy()] # Объединяем все в один кортеж
                
                obj_arr = _twiceschedule(obj)
                for i in range(len(obj_arr)):
                    obj_arr[i] = _weekslicer(obj_arr[i])

                schedule.extend(obj_arr) 
                evenodd += 1
                order += 0.5
            
            groups_schedule[find.group(1)][k] = schedule
        
        # Делаем срез для субботы
        day_lesson = sheet.col_values(col - 1, start_rowx=93, end_rowx=105)
        type_lesson = sheet.col_values(col, start_rowx=93, end_rowx=105)
        audit_lesson = sheet.col_values(col + 2, start_rowx=93, end_rowx=105)
        for i in range(len(day_lesson)): # Убираем плхие символы и т.д.
            day_lesson[i] = _antidot(day_lesson[i], 1)
            day_lesson[i] = _substitute(day_lesson[i])
            type_lesson[i] = _antidot(type_lesson[i])
            audit_lesson[i] = _antidot(audit_lesson[i])
        
        evenodd = 1
        schedule = []
        time_iter = iter(time_schedule)
        for i in range(len(day_lesson)):
            lesson = day_lesson[i]
            typ = type_lesson[i]
            audit = audit_lesson[i] 
            time = next(time_iter)
            if evenodd % 2 == 0:
                eo = "EVEN"
            else:
                eo = "ODD"
            obj = [lesson, typ, audit, time[0], time[1], int(order), eo, week.copy()] # Объединяем все в один кортеж
            
            obj_arr = _twiceschedule(obj)
            for i in range(len(obj_arr)):
                obj_arr[i] = _weekslicer(obj_arr[i])

            schedule.extend(obj_arr) 
            evenodd += 1
            order += 0.5
        groups_schedule[find.group(1)][5] = schedule

    

    # --- Основная часть функции --- #

    if _check_tags(cfg.block_tags, xlfilename) != None:
        return None

    groups_schedule = {} # Расписание каждой группы    
    time_schedule = [] # Раписание для текущего файла
    # * Открываем эксель таблицу * # 
    rb = xlrd.open_workbook("./xl/" + xlfilename)
    sheet = rb.sheet_by_index(0)
    
    col = 0
    now_tag = _check_tags(special_tags, xlfilename)

    if now_tag == "Маг" or now_tag == "маг":
        start_slice = sheet.col_values(2, start_rowx=3, end_rowx=21)
        end_slice = sheet.col_values(3, start_rowx=3, end_rowx=21)
    else:
        start_slice = sheet.col_values(2, start_rowx=3, end_rowx=15)
        end_slice = sheet.col_values(3, start_rowx=3, end_rowx=15)

    for time in start_slice:
        if time != '':
            time_schedule.append(time)
        else:
            time_schedule.append(time_schedule[len(time_schedule) - 1])
    i = 0
    for time in end_slice:
        if time != '':
            time_schedule[i] = (time_schedule[i], time)
        else:
            time_schedule[i] = time_schedule[i - 1]
        i += 1

    
    # * Крутим все группы, заполняем расписание * #
    for now_val in sheet.row_values(1):
        try:
            find = re.search(r".*(....-\d{2}-\d{2}).*", now_val)
            if find == None:
                raise Exception
        except:
            col += 1
        else:
            col += 1
            groups_schedule[find.group(1)] = [[], [], [], [], [], []] # ! Записывает только имя группы. Все спецобозначения откидываются

            if now_tag == "Маг" or now_tag == "маг":
                _mag_handler()
            else:
                _default_handler()

    return groups_schedule

def convert_in_json(data, filename):
    '''
    Преобразует python-данные в формат json.
    '''
    try:    
        os.makedirs("json")
    except:
        pass
    with open("./json/" + filename, "w", encoding="utf-8") as f:
        json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)  

def convert_in_postgres(group_schedule):
    '''
    Записывает в базу PostgreSQL расписание группы. Сначала 
    '''
    global _ident
    days = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА"]
    days_iter = iter(days)

    for group in group_schedule.keys():
        days_iter = iter(days)
        for day in group_schedule[group]:
            day_now = next(days_iter)
            for lesson_info in day:
                lesson, typ, audit, start_time, end_time, order, even, week = lesson_info
                
                strweek = [str(i) for i in week]
                strweek = "{" + ",".join(strweek) + "}"
                
                
                idn = str(_ident)
                tm.insert_lesson(idn, group, day_now, lesson, typ, audit, start_time, end_time, order, even, strweek)
                _ident += 1


if __name__ == "__main__":
    _ident = 0

    update_MireaSchedule()
    today = date.today()
    print(today)
    
    schedule = get_WeekSchedule(today, 'ККСО-01-19')
    print(schedule)
    pass
    