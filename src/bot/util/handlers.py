import datetime
import re
from datetime import date

from aiogram import types
import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler
from aiogram.utils.markdown import bold, escape_md, text
from loguru import logger

from util.helpers import *
from util.keyboards import craft_paging_keyboard, craft_startup_keyboard
from util.middleware import check_state
from util.settings import ADMINS, db, dp, bot
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
        keyboard = craft_startup_keyboard()
        await message.answer(text, reply_markup=keyboard)
    else:
        # Creating a user state in memory to avoid constant database requests
        state = dp.current_state(user=message.from_user.id)
        await state.update_data(group=result, page=date.today())

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
        await state.update_data(group=find_group.group(0).upper())
        user_data = await state.get_data()

        await message.answer(f"Группа: {escape_md(user_data['group'])} успешно установлена\!")

        user = 'Null'

        if message.from_user.username != None:
            user = message.from_user.username

        db.insert_user(
            tgid=message.from_user.id,
            username=user,
            first_name=message.from_user.first_name,
            lang=message.from_user.language_code,
            group=user_data['group']
        )
        logger.info(f"User successfully registered: {message.from_user.first_name} with group {user_data['group']}")
        await state.reset_state(with_data=False)
    else:
        await state.update_data(group=find_group.group(0).upper())
        user_data = await state.get_data()
        db.update_user_info(tgid=message.from_user.id, group=user_data['group'])
        await message.answer(f"Группа: {escape_md(user_data['group'])} успешно обновлена\!")
        logger.info(f"Group updated for user {message.from_user.id}")
        await state.reset_state(with_data=False)

@dp.message_handler(regexp='^Сегодня$')
@dp.message_handler(commands='today', state='*')
async def get_today(message: types.Message):
    logger.info(f'User {message.from_user.id} request today schedule')

    state = dp.current_state(user=message.from_user.id)

    if not await check_state(message, state):
        raise CancelHandler()

    user_data = await state.get_data()
    group = user_data['group']
    text = craft_schedule(group, mode=0)
    keyboard = craft_startup_keyboard()
    await message.answer(text, reply_markup=keyboard)

@dp.message_handler(regexp='^Завтра$')
@dp.message_handler(commands='next', state='*')
async def get_tomorrow(message: types.Message):
    logger.info(f'User {message.from_user.id} request tomorrow schedule')
    state = dp.current_state(user=message.from_user.id)

    if not await check_state(message, state):
        raise CancelHandler()

    user_data = await state.get_data()
    group = user_data['group']
    text = craft_schedule(group, mode=1)
    await message.answer(text)

@dp.message_handler(regexp='^Неделя$')
@dp.message_handler(commands='week', state='*')
async def get_week(message: types.Message):
    logger.info(f'User {message.from_user.id} request week schedule')
    state = dp.current_state(user=message.from_user.id)

    if not await check_state(message, state):
        raise CancelHandler()

    user_data = await state.get_data()
    group = user_data['group']
    text = craft_schedule(group, mode=2)
    await message.answer(text)

@dp.message_handler(commands='update', state='*')
async def update_user_group(message: types.Message, state: FSMContext):
    await message.answer('Хорошо, укажите вашу группу')
    await state.set_state(User.group)

@dp.message_handler(commands='getweek')
async def get_current_week(message: types.Message):
    logger.info(f'User {message.from_user.id} request get week')
    text = craft_week_message()
    await message.answer(text)

@dp.message_handler(commands='time')
async def get_time_schedule(message: types.Message):
    logger.info(f'User {message.from_user.id} request time')
    state = dp.current_state(user=message.from_user.id)

    if not await check_state(message, state):
        raise CancelHandler()

    user_data = await state.get_data()
    group = user_data['group']
    text = craft_time_schedule(group)
    await message.answer(text)

@dp.message_handler(commands='me')
async def get_user_profile(message: types.Message):
    logger.info(f'User {message.from_user.id} request themself profile')
    state = dp.current_state(user=message.from_user.id)

    if not await check_state(message, state):
        raise CancelHandler()

    user_data = await state.get_data()
    group= user_data['group']
    
    text = craft_user_profile(message, group)
    await message.answer(text)

@dp.message_handler(commands='dev')
async def show_developers(message: types.Message):
    logger.info(f'User {message.from_user.id} request developer info')

    data = text(
        "Разработчик интерфейса: ",
        bold("@delvinru"),
        "\nРазработчик парсера: ",
        bold("@ozzero"),
        "\nПо любым вопросам, предложениям по улучшению бота, можно писать в личку\.",
        sep = ""
    )
    await message.answer(data)

@dp.callback_query_handler(text='prev_week')
async def process_prev_week(query: types.CallbackQuery):
    logger.info(f'User {query.from_user.id} request decrease a page')

    state = dp.current_state(user=query.from_user.id)

    # Check state
    if not await check_state(query, state):
        raise CancelHandler()

    user_data = await state.get_data()

    # Decrease weeks
    current_week = user_data['page']
    if not (parser.get_WeekNumber(current_week) <= 1):
        current_week -= datetime.timedelta(days=7)
    
    await state.update_data(page=current_week)
    text = craft_schedule(user_data['group'], mode=2, special_date=current_week)
    keyboard = craft_paging_keyboard()

    # Catch if user got border
    try:
        await query.message.edit_text(text, reply_markup=keyboard)
        await bot.answer_callback_query(query.id)
    except aiogram.utils.exceptions.MessageNotModified:
        await bot.answer_callback_query(query.id, text='Вы достигли начала расписания\nДальше двигаться некуда', show_alert=True)

@dp.callback_query_handler(text='next_week')
async def process_next_week(query: types.CallbackQuery):
    logger.info(f'User {query.from_user.id} request increase a page')

    state = dp.current_state(user=query.from_user.id)
    user_data = await state.get_data()

    # Check state
    if not await check_state(query, state):
        raise CancelHandler()

    # Increase weeks
    # current_week = user_data['page'] + datetime.timedelta(days=7)
    current_week = user_data['page']
    if not (parser.get_WeekNumber(current_week) >= 17):
        current_week += datetime.timedelta(days=7)
    
    await state.update_data(page=current_week)
    text = craft_schedule(user_data['group'], mode=2, special_date=current_week)
    keyboard = craft_paging_keyboard()
    try:
        await query.message.edit_text(text, reply_markup=keyboard)
        await bot.answer_callback_query(query.id)
    except aiogram.utils.exceptions.MessageNotModified:
        await bot.answer_callback_query(query.id, text='Вы достигли конца расписания\nДальше двигаться некуда', show_alert=True)


@dp.message_handler(commands='pages', state='*')
async def show_week_page(message: types.Message):
    logger.info(f'User {message.from_user.id} request a pages function')

    state = dp.current_state(user=message.from_user.id)

    if not await check_state(message, state):
        raise CancelHandler()
    
    user_data = await state.get_data()
    group = user_data['group']

    # Setup for user
    text = craft_schedule(group, mode=2)
    keyboard = craft_paging_keyboard()

    # Update page state
    today = date.today()
    if today.weekday() == 6:
        today += datetime.timedelta(days=1)

    await state.update_data(page=today)
    await message.answer(text, reply_markup=keyboard)

@dp.message_handler(commands='update_db')
async def admin_update_db(message: types.Message):
    """ Admin feature for update database """
    logger.info(f'User {message.from_user.id} request admin feauture')
    if message.from_user.id not in ADMINS:
        return await message.answer(escape_md("Извини, но у тебя нет прав на это!🤷‍♂️"))

    await message.answer(escape_md('Начал обновлять базу. Это может занять некоторое время...'))
    try:
        parser.update_MireaSchedule()
    except:
        await message.answer('Что-то пошло не так/!')
    else:
        await message.answer('База данных успешно обновлена\!')
