import asyncio
import io
import logging
import os
import random
import re
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import MessageEntityType, ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, FSInputFile, Message
from cheburek_core import Chain, MemeGenerator
from dotenv import load_dotenv

load_dotenv()

chain = Chain()
meme_gen = MemeGenerator()

dp = Dispatcher()


@dp.message(Command("stats"))
async def stats(message: Message):
    guild_id = str(message.chat.id)

    words = chain.get_words_count(guild_id)
    links = chain.get_links_count(guild_id)

    answer = f"{html.bold(f"Статистика для канала {message.chat.full_name}:")}\n📖 Слова – {words} слов\n🔗 Связей – {links} связей"
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
    guild_id = str(message.chat.id)

    if chain.get_words_count(guild_id) == 0:
        await message.answer(
            html.bold(
                "❌ Не хватает слов! Отправьте больше сообщений и повторите команду."
            )
        )
        return

    msg = chain.generate_message(random.randint(2, 8), guild_id)
    img = meme_gen.create_fresco(msg)

    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)

        photo_to_send = BufferedInputFile(
            image_binary.getvalue(), filename="fresco.png"
        )
        await message.answer_photo(photo=photo_to_send)


@dp.message()
async def on_message(message: Message, bot: Bot):
    guild_id = str(message.chat.id)

    if message.text:
        clean_content = re.sub(
            r"https?:\/\/[^\s)\]]+",
            "",
            message.text,
        )
        clean_content = re.sub(r"<@!?\d+>", "", clean_content)
        clean_content = re.sub(r"\s+", " ", clean_content).strip()

        words = clean_content.split(" ")
        chain.process_words(words, guild_id)

    is_mentioned = False

    me = await bot.get_me()
    bot_mention = f"@{me.username}".casefold()

    if message.entities and message.text:
        for entity in message.entities:
            if entity.type == MessageEntityType.MENTION:
                mentioned = message.text[entity.offset : entity.offset + entity.length]

                if mentioned.casefold() == bot_mention:
                    is_mentioned = True
                    break

    if is_mentioned or random.random() < float(os.environ["MESSAGE_CHANCE"]):
        msg = chain.generate_message(random.randint(2, 12), guild_id)
        await message.reply(msg)


async def main():
    bot = Bot(
        token=os.environ["TOKEN"],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
