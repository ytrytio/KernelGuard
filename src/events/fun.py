from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import aiohttp

router = Router(name=__name__)

async def fetch_json(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@router.message(Command("cat"))
async def cat(message: Message):
    data = await fetch_json("https://api.thecatapi.com/v1/images/search")
    url = data[0]["url"]
    await message.reply_photo(url, allow_sending_without_reply=True)

@router.message(Command("catgif"))
async def catgif(message: Message):
    #data = await fetch_json("https://cataas.com/cat/gif?json=true")
    #url = data["url"]
    #if not url.startswith("http"):
    #    url = f"https://cataas.com{url}"
    #await message.reply_animation(url, allow_sending_without_reply=True)
    await message.reply("Not available.")

@router.message(Command("neko"))
async def neko(message: Message):
    data = await fetch_json("https://nekos.best/api/v2/neko")
    url = data['results'][0]['url']
    await message.reply_photo(url, allow_sending_without_reply=True)

@router.message(Command("waifu"))
async def waifu(message: Message):
    data = await fetch_json("https://nekos.best/api/v2/waifu")
    url = data['results'][0]['url']
    await message.reply_photo(url, allow_sending_without_reply=True)
