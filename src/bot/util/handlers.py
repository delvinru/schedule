import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import escape_md
from loguru import logger
from pprint import pprint

from util.settings import dp, db
from util.states import *
from util.helpers import *

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
        # TODO: show schdule for today
        # TODO: save user group in user state
        await message.answer(f"Your group: {escape_md(result)}")


@dp.message_handler(state=User.group)
async def process_group(message: types.Message, state: FSMContext):

    if re.search(r"\b\w{4}-\d{2}-\d{2}\b", message.text) == None:
        await message.answer("Пожалуйста, укажите группу в правильном формате\!")
        return

    await state.update_data(group=message.text.upper())
    user_data = await state.get_data()

    await message.answer(f"Группа: {escape_md(user_data['group'])} успешно установлена\!")
    db.insert_user(tgid=message.from_user.id, group=user_data['group'])
    logger.info(f"User successfully registered: {message.from_user.first_name} with group {user_data['group']}")
    await state.finish()

@dp.message_handler(commands='today')
async def get_today(message: types.Message):
    # TODO: fix this shit way for getting group
    result = db.get_user_group(tgid=message.from_user.id)
    text = craft_schedule(result, 0)
    await message.answer(escape_md(text))

@dp.message_handler(commands='next')
async def get_tomorrow(message: types.Message):
    # TODO: fix this shit way for getting group
    result = db.get_user_group(tgid=message.from_user.id)
    text = craft_schedule(result, 1)
    await message.answer(escape_md(text))

@dp.message_handler(commands='week')
async def get_week(message: types.Message):
    # TODO: fix this shit way for getting group
    result = db.get_user_group(tgid=message.from_user.id)
    text = craft_schedule(result, 2)
    await message.answer(escape_md(text))
