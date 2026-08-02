from aiogram import Bot, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from ..utils.helpers import *
from ..config import GROUP, ADMINS

router = Router(name=__name__)

@router.message(Command("punish"))
async def punish(message: Message, bot: Bot):
    if not message.reply_to_message: return await message.reply("Try writing in reply to a message.")
    if message.from_user is None or message.reply_to_message.from_user is None: return

    chat_id = message.chat.id
    chat_type = message.chat.type
    user_id = message.from_user.id
    victim_id = message.reply_to_message.from_user.id
    victim_link = message.reply_to_message.from_user.mention_html()
    user_link = message.from_user.mention_html()

    if user_id not in ADMINS: return await message.reply("Are you sure you have enough rights?")
    if victim_id in ADMINS: return await message.reply("Don't try to punish my master.")

    if not await check(chat_type, chat_id, message): return
    else:
        await bot.restrict_chat_member(
            GROUP,
            user_id=victim_id,
            permissions=get_permissions(False)
        )
        await message.reply(
            f"{victim_link} was punished by {user_link} for his bad behavior.",
            allow_sending_without_reply=True,
            parse_mode="HTML"
        )

@router.message(Command("ban"))
async def ban(message: Message, bot: Bot):
    if not message.reply_to_message: return await message.reply("Try writing in reply to a message.")
    if message.from_user is None or message.reply_to_message.from_user is None: return

    chat_id = message.chat.id
    chat_type = message.chat.type
    user_id = message.from_user.id
    victim_id = message.reply_to_message.from_user.id
    victim_link = message.reply_to_message.from_user.mention_html()
    user_link = message.from_user.mention_html()

    if user_id not in ADMINS: return await message.reply("Are you sure you have enough rights?")
    if victim_id in ADMINS: return await message.reply("Don't try to ban my master.")

    if not await check(chat_type, chat_id, message): return
    else:
        await message.chat.ban(victim_id)
        await message.reply(
            f"{victim_link} was banned by {user_link}.",
            allow_sending_without_reply=True,
            parse_mode="HTML"
        )

@router.message(Command("normal"))
async def normal(message: Message, bot: Bot):
    if not message.reply_to_message: return await message.reply("Try writing in reply to a message.")
    if message.from_user is None or message.reply_to_message.from_user is None: return

    chat_id = message.chat.id
    chat_type = message.chat.type
    user_id = message.from_user.id
    victim_id = message.reply_to_message.from_user.id
    victim_link = message.reply_to_message.from_user.mention_html()
    user_link = message.from_user.mention_html()

    if user_id not in ADMINS: return await message.reply("Are you sure you have enough rights?")

    if not await check(chat_type, chat_id, message): return
    else:
        await bot.restrict_chat_member(
            GROUP,
            user_id=victim_id,
            permissions=get_permissions(True)
        )
        await message.reply(
            f"{victim_link} was recognized by {user_link} in our community.",
            allow_sending_without_reply=True,
            parse_mode="HTML"
        )

@router.message(Command("unban"))
async def unban(message: Message, bot: Bot):
    if not message.reply_to_message: return await message.reply("Try writing in reply to a message.")
    if message.from_user is None or message.reply_to_message.from_user is None: return

    chat_id = message.chat.id
    chat_type = message.chat.type
    user_id = message.from_user.id
    victim_id = message.reply_to_message.from_user.id
    victim_link = message.reply_to_message.from_user.mention_html()
    user_link = message.from_user.mention_html()

    if user_id not in ADMINS: return await message.reply("Are you sure you have enough rights?")

    if not await check(chat_type, chat_id, message): return
    else:
        await message.chat.unban(victim_id)
        await message.reply(
            f"{victim_link} was unbanned by {user_link}",
            allow_sending_without_reply=True,
            parse_mode="HTML"
        )
