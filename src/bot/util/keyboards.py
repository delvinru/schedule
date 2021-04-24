from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)


def craft_startup_keyboard() -> ReplyKeyboardMarkup:
    """
    Method for crafting startup keyboard with function /today, /next, /week
    """

    buttons = [
        KeyboardButton('Сегодня'),
        KeyboardButton('Завтра'),
        KeyboardButton('Неделя')
    ]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(*buttons)
    return keyboard

def craft_paging_keyboard() -> InlineKeyboardMarkup:
    """
    Method for crafting paging keyboard in paging menu
    """

    buttons = [
        InlineKeyboardButton('◀️', callback_data='prev_week'),
        InlineKeyboardButton('▶️', callback_data='next_week')
    ]
    keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
    return keyboard
