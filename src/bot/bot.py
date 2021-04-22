import asyncio
import sys

from loguru import logger

from util.handlers import *
from aiogram import Bot
from aiogram.types import BotCommand
from util.settings import dp, bot
import xlparser.parser as parser


async def set_commands(bot: Bot):
    """ Register command for Telegram interface """

    commands = [
        BotCommand(command='/start', description='Начать взаимодействие с ботом'),
        BotCommand(command='/today', description='Узнать расписание на сегодня'),
        BotCommand(command='/next', description='Узнать расписание на завтра'),
        BotCommand(command='/week', description='Узнать расписание на неделю')
    ]
    await bot.set_my_commands(commands)

async def main():
    """ Start long polling """
    # Setup bot commands
    await set_commands(bot)
    # Start long pollings for bot
    await dp.start_polling()

if __name__ == "__main__":
    # Set base logging
    logger.remove()
    logger.add(
        "logs/debug.log",
        format="[{time:YYYY-MM-DD HH:mm:ss}] {level} | {message}",
        level="DEBUG",
        rotation="1 MB")
    logger.add(sys.__stdout__)

    asyncio.run(main())
