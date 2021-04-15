import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = os.getenv('API_TOKEN') or ''

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.MARKDOWN_V2)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)