import asyncio
import logging
import os
import random
import re
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from cheburek import Chain, MemeGenerator
from dotenv import load_dotenv

load_dotenv()

chain = Chain()
meme_gen = MemeGenerator()

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    if not message.from_user:
        return

    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}")


@dp.message(Command("stats"))
async def stats(message: Message):
    guild_id = str(message.chat.id)

    words = chain.get_words_count(guild_id)
    links = chain.get_links_count(guild_id)
    images = meme_gen.get_images_count(guild_id)

    answer = f"{html.bold(f"Статистика для канала {message.chat.full_name}:")}\n📖 Слова – {words} слов\n🔗 Связей – {links} связей\n🌅 Изображений – {images} изображений"
    await message.answer(answer)


@dp.message(Command("generate"))
async def generate(message: Message):
    guild_id = str(message.chat.id)

    if chain.get_words_count(guild_id) == 0:
        await message.answer(
            html.bold(
                "❌ Не хватает слов! Отправьте больше сообщений и повторите команду."
            )
        )
        return

    msg = chain.generate_message(random.randint(2, 12), guild_id)
    await message.answer(msg)


@dp.message(Command("fresco"))
async def fresco(message: Message):
    pass


@dp.message(Command("demotivator"))
async def demotivator(message: Message):
    pass


@dp.message(Command("meme"))
async def meme(message: Message):
    pass


@dp.message()
async def on_message(message: Message):
    if message.text:
        clean_content = re.sub(
            r"https?:\/\/[^\s)\]]+",
            "",
            message.text,
        )
        clean_content = re.sub(r"<@!?\d+>", "", clean_content)
        clean_content = re.sub(r"\s+", " ", clean_content).strip()

        words = clean_content.split(" ")
        chain.process_words(words, str(message.chat.id))


async def main():
    bot = Bot(
        token=os.environ["TOKEN"],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
