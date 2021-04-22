import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db.tablemanager import Database

TOKEN = os.getenv('API_TOKEN') or ''

pg_db = os.getenv('POSTGRES_DB') or ''
pg_user = os.getenv('POSTGRES_USER') or ''
pg_pwd = os.getenv('POSTGRES_PASSWORD') or ''
pg_host = 'database'
pg_port = '5432'

ADMINS = [258229531, 292051709]

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.MARKDOWN_V2)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = Database(database=pg_db, user=pg_user, password=pg_pwd, host=pg_host, port=pg_port)
db.init_table()