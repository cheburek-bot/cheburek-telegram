import asyncio
import io
import logging
import os
import random
import re
import sys
import uuid
from pathlib import Path
from typing import final

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import MessageEntityType, ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, FSInputFile, Message
from cheburek_core import AnimationGenerator, Chain, MemeGenerator
from dotenv import load_dotenv

load_dotenv()

chain = Chain(start_word_type=os.environ["START_WORD_TYPE"])
meme_gen = MemeGenerator()
anim_gen = AnimationGenerator()

dp = Dispatcher()


@dp.message(Command("stats"))
async def stats(message: Message):
    guild_id = str(message.chat.id)

    words = chain.get_words_count(guild_id)
    links = chain.get_links_count(guild_id)
    images = meme_gen.get_images_count(guild_id)
    anims = anim_gen.get_animations_count(guild_id)

    answer = f"{html.bold(f"Статистика для канала {message.chat.full_name}:")}\n📖 Слова – {words} слов\n🔗 Связей – {links} связей\n🌅 Изображений – {images} изображений\n🎬 Гифки – {anims} гифок"
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


@dp.message(Command("demotivator"))
async def demotivator(message: Message):
    guild_id = str(message.chat.id)

    if meme_gen.get_images_count(guild_id) == 0:
        await message.answer(
            html.bold(
                "❌ Не хватает изображений! Отправьте больше изображений и повторите команду."
            )
        )
        return

    if chain.get_words_count(guild_id) == 0:
        await message.answer(
            html.bold(
                "❌ Не хватает слов! Отправьте больше сообщений и повторите команду."
            )
        )
        return

    random_img = meme_gen.get_random_image_path(guild_id)

    msg = chain.generate_message(random.randint(2, 8), guild_id)
    img = meme_gen.create_demotivator(msg, random_img)

    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)

        photo_to_send = BufferedInputFile(
            image_binary.getvalue(), filename="demotivator.png"
        )
        await message.answer_photo(photo=photo_to_send)


@dp.message(Command("meme"))
async def meme(message: Message):
    guild_id = str(message.chat.id)

    if meme_gen.get_images_count(guild_id) == 0:
        await message.answer(
            html.bold(
                "❌ Не хватает изображений! Отправьте больше изображений и повторите команду."
            )
        )
        return

    if chain.get_words_count(guild_id) == 0:
        await message.answer(
            html.bold(
                "❌ Не хватает слов! Отправьте больше сообщений и повторите команду."
            )
        )
        return

    msg1 = chain.generate_message(random.randint(2, 8), guild_id)
    msg2 = chain.generate_message(random.randint(2, 8), guild_id)

    random_img = meme_gen.get_random_image_path(guild_id)

    img = meme_gen.create_meme(msg1, msg2, random_img)

    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)

        photo_to_send = BufferedInputFile(image_binary.getvalue(), filename="meme.png")
        await message.answer_photo(photo=photo_to_send)


@dp.message(Command("ameme"))
async def ameme(message: Message):
    guild_id = str(message.chat.id)

    if anim_gen.get_animations_count(guild_id) == 0:
        await message.answer(
            html.bold(
                "❌ Не хватает гифок! Отправьте больше гифок и повторите команду."
            )
        )
        return

    if chain.get_words_count(guild_id) == 0:
        await message.answer(
            html.bold(
                "❌ Не хватает слов! Отправьте больше сообщений и повторите команду."
            )
        )
        return

    msg1 = chain.generate_message(random.randint(2, 8), guild_id)
    msg2 = chain.generate_message(random.randint(2, 8), guild_id)

    random_anim = anim_gen.get_random_animation(guild_id)

    temp_path = Path(f"data/{guild_id}/temp")
    temp_path.mkdir(parents=True, exist_ok=True)

    id = uuid.uuid4().hex
    output_path = f"{temp_path}/output_{id}.mp4"

    await asyncio.to_thread(
        anim_gen.create_animated_meme, msg1, msg2, random_anim, output_path
    )

    try:

        video_file = FSInputFile(output_path)
        await message.answer_video(video_file)
    except Exception as e:
        print(e)
        await message.answer(html.bold("❌ Произошла ошибка!"))
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


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

    if message.photo:
        image_dir = Path(f"./data/{guild_id}/images")
        image_dir.mkdir(parents=True, exist_ok=True)

        photo = message.photo[-1]
        destination = image_dir / photo.file_unique_id
        await bot.download(photo, destination=destination)
        return

    if message.animation:
        gif_dir = Path(f"./data/{guild_id}/gifs")
        gif_dir.mkdir(parents=True, exist_ok=True)

        gif = message.animation
        destination = gif_dir / gif.file_unique_id
        await bot.download(gif, destination=destination)
        return

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
