### Главное
```python
def update_MireaSchedule()
```
Обновляет базу данных, подгружая актуальные файлы с сайта расписания МИРЭА. Обрабатывает их и записывает обработанные данные в JSON и PostgreSQL. Перед этим удаляет старые записи в базе данных.
Функция очень времязатратная, поэтому советуется запускать её в ручном режиме (только когда есть необходимость).

```python
def get_TodaySchedule(today, group)
def get_TomorrowSchedule(today, group)
def get_WeekSchedule(today, group)
```
Возвращает список с расписанием группы на сегодня, завтра или на текущую неделю в следующем формате:
```python
schedule = [ident, lesson, typ, audit, start_time, end_time, order, even, week]
# 0 - ident        - идентификатор занятия в базе данных
# 1 - group        - название группы
# 2 - day          - день недели
# 3 - lesson       - названия занятия
# 4 - typ          - тип занятия (лк/пр/лаб)
# 5 - audit        - аудитория занятия
# 6 - start_time   - время начала занятия
# 7 - end_time     - время конца занятия
# 8 - order        - номер занятия за день (1 = первая пара)
# 9 - even         - четность недели
#10 - week         - недели, на которых проходят занятия
```
Parser проверяет, что занятия точно проводятся на этой недели, повторную проверку проводить не нужно. Однако, стоит проверять, что все пары (с 1 до 6-8) есть в списке.

Формат входных данных:
```python
group = 'AAAA-12-12' # Строка формата (4 буквы)-(2 цифры)-(2 цифры)
today = date.today() # Результат функции today() из библиотеки datetime
```

```python
def get_WeekNumber(today)
```
Возвращает номер текущей недели

```python
def check_GroupExist(grp)
```
Возвращает True, если группа есть в базе, и False в противном случае

### Другое
```python
def get_links(link, filename="links.txt")
# link          - ссылка на исходный сайт
# filename      - имя файла, в который будет записаны найденные ссылки
```
Достает из html-страницы сайта все ссылки на xlsx файлы.

```python
def get_xlfiles(filename="links.txt")
# filename      - имя файла, в котором лежат все ссылки на xl-файлы
```
Скачивает все xlsx файлы по ссылкам и складывает их в одну папку.

```python
def parse_xlfiles(xlfilename, block_tags=[], special_tags=[], substitute_lessons=[])
# xlfilename    - имя xl-файла
# block_tags    - теги в именах файла, обработку которых проводить не нужно
# special_tags  - ключевые теги в именах файлах, для которых существует специальный обработчик
# substitute_lessons - список замен
```
Обработчик xl-Файлов. Возвращает рассписание всех групп из файла.

```python
def convert_in_json(data, filename)
# data          - python-данные
# filename      - xlsx файл, из которого получены данные

def convert_in_postgres(group_schedule, con)
# group_schedule- рассписание группы
# con           - дискриптор соединения с базой данных
```
Записывает данные в JSON или POSTGRES.

### TODO:
- [x] Add README for Parser
- [x] Connection to base using Class
- [x] Use to connection environment variable
- [ ] Short form of long-named lesson
- [ ] One permanent or Much short-time connection to base?
- [ ] Think about rational storage use (needed .json and .xlsx in permanent storage? 🤔)