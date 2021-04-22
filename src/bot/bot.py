import asyncio
import sys

from loguru import logger

from util.handlers import *
from util.settings import dp
import xlparser.parser as parser



async def main():
    """ Start long polling """

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
