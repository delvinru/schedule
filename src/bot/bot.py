import sys

from aiogram import executor
from loguru import logger

from util.settings import dp, bot
from util.handlers import *


def main():
    """ Start long polling """

    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    # Set base logging
    logger.remove()
    logger.add(
        "logs/debug.log",
        format="[{time:YYYY-MM-DD HH:mm:ss}] {level} | {message}",
        level="DEBUG",
        rotation="1 MB")
    logger.add(sys.__stdout__)

    main()
