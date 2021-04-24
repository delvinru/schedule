""" States for bot context """
from aiogram.dispatcher.filters.state import State, StatesGroup

class User(StatesGroup):
    group = State()
    page = State()

class Feedback(StatesGroup):
    text = State()