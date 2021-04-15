import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import escape_md
from loguru import logger

from util.settings import dp
from util.states import *


@dp.message_handler(commands='start')
async def start(message: types.Message):
    text = """
Привет, это бот с расписанием для РТУ МИРЭА\!\n
Для начала работы отправь мне свою группу\.
    """
    await User.group.set()

    logger.info(f"User came to registration menu: {message.from_user.first_name}")

    await message.answer(text)

@dp.message_handler(state=User.group)
async def process_group(message: types.Message, state: FSMContext):

    if not re.findall(r"\w{4}-\d{2}-\d{2}", message.text):
        await message.answer("Пожалуйста, укажите группу в правильном формате\!")
        return

    await state.update_data(group=message.text.upper())

    user_data = await state.get_data()

    await message.answer(f"Группа: {escape_md(user_data['group'])} успешно установлена\!")

    logger.info(f"User successfully registered: {message.from_user.first_name} with group {user_data['group']}")

    await state.finish()
