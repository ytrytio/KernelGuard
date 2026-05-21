from aiogram import Bot, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from ..utils.helpers import *
from ..config import GROUP, ADMINS

router = Router(name=__name__)

@router.message(Command("selfharm"))
async def selfharm(message: Message, bot: Bot):
    if message.from_user is None: return

    chat_id = message.chat.id
    chat_type = message.chat.type
    user_id = message.from_user.id
    user_link = message.from_user.mention_html()

    if user_id in ADMINS: 
        return await message.reply("Don't try to punish my master (even if it's yourself).")

    if not await check(chat_type, chat_id, message): return
    
    try:
        await bot.restrict_chat_member(
            GROUP,
            user_id=user_id,
            permissions=get_permissions(False)
        )
        await message.reply(
            f"{user_link} punished themselves for bad behavior.",
            allow_sending_without_reply=True,
            parse_mode="HTML"
        )
    except Exception as e:
        await message.reply(f"Failed to punish you. Error: {e}")


@router.message(Command("suicide"))
async def suicide(message: Message, bot: Bot):
    if message.from_user is None: return

    chat_id = message.chat.id
    chat_type = message.chat.type
    user_id = message.from_user.id
    user_link = message.from_user.mention_html()

    if user_id in ADMINS: 
        return await message.reply("The master cannot commit suicide. You are needed here.")

    if not await check(chat_type, chat_id, message): return

    try:
        await message.reply(
            f"{user_link} has decided to end it all.",
            allow_sending_without_reply=True,
            parse_mode="HTML"
        )
        
        await change_prefix(bot, message.chat, user_id)
        
        import time
        until_date = int(time.time()) + 60
        
        await message.chat.ban(user_id, until_date=until_date)
        
    except Exception as e:
        await message.reply(f"Failed to kill you. Error: {e}")
