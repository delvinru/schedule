from datetime import date
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import escape_md

from util.settings import db


async def check_state(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    user_data = await state.get_data()
    # Check if bot was restarted and in state not saved group
    if not user_data.get('group'):
        group = db.get_user_group(tgid=message.from_user.id)
        if not group:
            await message.answer(
                escape_md((
                    'Сначала зарегистрируйся, иначе как я узнаю твою группу?🤔'
                    '\nНажми сюда: /start'
                    )))
            return False
        await state.update_data(group=group, page=date.today())
    return True
