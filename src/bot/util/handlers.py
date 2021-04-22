import re

import xlparser.parser as parser
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import escape_md
from loguru import logger

from util.helpers import *
from util.settings import ADMINS, db, dp
from util.states import *


@dp.message_handler(commands='start')
async def start(message: types.Message):
    """ Start message """

    text = "Привет, это бот с расписанием для РТУ МИРЭА\!\n"
    append = "Для начала работы отправь мне свою группу\."

    # If we get new user ask for registration
    result = db.get_user_group(tgid=message.from_user.id)
    logger.info(f'Got res: {result}')
    if not result:
        text += append
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(User.group)

        logger.info(f"User came to registration menu: {message.from_user.first_name}")

        await message.answer(text)
    else:
        # Creating a user state in memory to avoid constant database requests
        state = dp.current_state(user=message.from_user.id)
        await state.update_data(group=result)
        # By default show today schedule
        await get_today(message, state)

@dp.message_handler(commands='cancel', state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer('Отмена регистрации')

@dp.message_handler(state=User.group)
async def process_group(message: types.Message, state: FSMContext):

    if re.search(r"\b\w{4}-\d{2}-\d{2}\b", message.text) == None:
        await message.answer("Пожалуйста, укажите группу в правильном формате\!")
        return

    await state.update_data(group=message.text.upper())
    user_data = await state.get_data()

    await message.answer(f"Группа: {escape_md(user_data['group'])} успешно установлена\!")
    db.insert_user(
        tgid=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        lang=message.from_user.language_code,
        group=user_data['group']
    )
    logger.info(f"User successfully registered: {message.from_user.first_name} with group {user_data['group']}")
    # await state.finish()


@dp.message_handler(commands='today', state='*')
async def get_today(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    group = user_data['group']
    text = craft_schedule(group, mode=0)
    await message.answer(escape_md(text))

@dp.message_handler(commands='next', state='*')
async def get_tomorrow(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    group = user_data['group']
    text = craft_schedule(group, mode=1)
    await message.answer(escape_md(text))

@dp.message_handler(commands='week', state='*')
async def get_week(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    group = user_data['group']
    text = craft_schedule(group, mode=2)
    await message.answer(escape_md(text))

@dp.message_handler(commands='update_db')
async def admin_feature(message: types.Message):
    """ Admin feature for update database """
    if message.from_user.id not in ADMINS:
        return await message.answer(escape_md("Извини, но у тебя нет прав на это!🤷‍♂️"))

    await message.answer(escape_md('Начал обновлять базу. Это может занять некоторое время...'))
    parser.update_MireaSchedule()
    await message.answer('База данных успешно обновлена\!')