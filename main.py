import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    if not message.from_user:
        return

    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}")


async def main():
    bot = Bot(
        token=os.environ["TOKEN"],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
