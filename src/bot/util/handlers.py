import re

import xlparser.parser as parser
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import escape_md
from loguru import logger

from util.helpers import *
from util.settings import ADMINS, db, dp
from util.states import *


@dp.message_handler(commands='start')
async def start(message: types.Message):
    """ Start message """

    # If we get new user ask for registration
    result = db.get_user_group(tgid=message.from_user.id)
    if not result:
        text = ("Привет, это бот с расписанием для РТУ МИРЭА\!✌️\n"
                "Для начала работы отправь мне свою группу\.")

        logger.info(f"User came to registration menu: {message.from_user.first_name}")
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(User.group)
        await message.answer(text)
    else:
        # Creating a user state in memory to avoid constant database requests
        state = dp.current_state(user=message.from_user.id)
        await state.update_data(group=result)

        # By default show today schedule
        await get_today(message)

@dp.message_handler(commands='cancel', state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer(escape_md('Регистрация в боте отменена!\nМожешь попробовать по новой: /start'))

@dp.message_handler(state=User.group)
async def process_group(message: types.Message, state: FSMContext):

    find_group= re.search(r"\b\w{4}-\d{2}-\d{2}\b", message.text.upper())
    if find_group == None:
        await message.answer("Пожалуйста, укажите группу в правильном формате\!")
        return
    
    if parser.check_GroupExist(find_group.group(0)) == False:
        await message.answer(escape_md("Твоя группа не найдена в нашей базе.🤷‍♂️\nПопробуй снова!"))
        return

    user_data = await state.get_data()
    if not user_data.get('group'):
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
        await state.reset_state(with_data=False)
    else:
        await state.update_data(group=message.text.upper())
        user_data = await state.get_data()
        db.update_user_info(tgid=message.from_user.id, group=user_data['group'])
        await message.answer(f"Группа: {escape_md(user_data['group'])} успешно обновлена\!")
        logger.info(f"Group updated for user {message.from_user.id}")
        await state.reset_state(with_data=False)

@dp.message_handler(commands='today', state='*')
async def get_today(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    user_data = await state.get_data()

    # Check if bot was restarted and in state not saved group
    if not user_data.get('group'):
        group = db.get_user_group(tgid=message.from_user.id)
        if not group:
            return await message.answer(escape_md('Сначала зарегистрируйся, иначе как я узнаю твою группу?🤔\nНажми сюда: /start'))
        await state.update_data(group=group)

    user_data = await state.get_data()
    logger.info(f'Today state: {user_data}')
    group = user_data['group']
    text = craft_schedule(group, mode=0)
    await message.answer(escape_md(text))

@dp.message_handler(commands='next', state='*')
async def get_tomorrow(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    user_data = await state.get_data()

    # Check if bot was restarted and in state not saved group
    if not user_data.get('group'):
        group = db.get_user_group(tgid=message.from_user.id)
        if not group:
            return await message.answer(escape_md('Сначала зарегистрируйся, иначе как я узнаю твою группу?🤔\nНажми сюда: /start'))
        await state.update_data(group=group)

    user_data = await state.get_data()
    group = user_data['group']
    text = craft_schedule(group, mode=1)
    await message.answer(escape_md(text))

@dp.message_handler(commands='week', state='*')
async def get_week(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    user_data = await state.get_data()

    # Check if bot was restarted and in state not saved group
    if not user_data.get('group'):
        group = db.get_user_group(tgid=message.from_user.id)
        if not group:
            return await message.answer(escape_md('Сначала зарегистрируйся, иначе как я узнаю твою группу?🤔\nНажми сюда: /start'))
        await state.update_data(group=group)

    user_data = await state.get_data()
    logger.info(f'Week state: {user_data}')
    group = user_data['group']
    text = craft_schedule(group, mode=2)
    await message.answer(escape_md(text))

@dp.message_handler(commands='update', state='*')
async def update_user_group(message: types.Message, state: FSMContext):
    await message.answer('Хорошо, укажите вашу группу')
    await state.set_state(User.group)

@dp.message_handler(commands='getweek')
async def get_current_week(message: types.Message):
    text = craft_week_message()
    await message.answer(text)


@dp.message_handler(commands='update_db')
async def admin_update_db(message: types.Message):
    """ Admin feature for update database """
    if message.from_user.id not in ADMINS:
        return await message.answer(escape_md("Извини, но у тебя нет прав на это!🤷‍♂️"))

    await message.answer(escape_md('Начал обновлять базу. Это может занять некоторое время...'))
    parser.update_MireaSchedule()
    await message.answer('База данных успешно обновлена\!')