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
schedule = [ident, lesson, typ, audit, order, even, week]
# ident        - идентификатор занятия в базе данных
# lesson       - названия занятий
# typ          - тип занятий (лк/пр/лаб)
# audit        - аудитория занятий
# order        - номер занятия за день (1 = первая пара)
# even         - четность недели
# week         - недели, на которых проходят занятия
```
Parser проверяет, что занятия точно проводятся на этой недели, повторную проверку проводить не нужно. Однако, стоит проверять, что все пары (с 1 до 6-8) есть в списке.

Формат входных данных:
```python
group = 'AAAA-12-12' # Строка формата (4 буквы)-(2 цифры)-(2 цифры)
today = date.today() # Результат функции today() из библиотеки datetime
```

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