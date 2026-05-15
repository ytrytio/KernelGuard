from aiogram import F, Router, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from time import time as unixtime

from ..storage.temp import pending_approvals
from ..config import GROUP
from ..utils.helpers import change_prefix

router = Router(name=__name__)

@router.message(F.text.in_({"Windows", "Linux", "MacOS"}), F.chat.type == "private")
async def handle_captcha_text(message: Message, bot: Bot):
    global pending_approvals
    if not message.from_user: return
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_answer = message.text
    link = message.from_user.mention_html() 
    
    if user_id not in pending_approvals:
        return await message.answer("Your join requests can not be found. \nWrite @cyber_glor in private, if you don't think so.", reply_markup=ReplyKeyboardRemove())

    chat_id = pending_approvals[user_id]
    until_ban = int(unixtime() + 86400)

    try:
        if user_answer == "Linux":
            await bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
            await message.answer(
                f"Nice job, homie. Welcome to <a href=\"https://t.me/c/2500557416\">Kernel Syndicate</a>!",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="HTML"
            )
            await bot.send_message(
                GROUP, 
                f"Welcome to Kernel Syndicate, {link}!",
                parse_mode="HTML"
            )
            await change_prefix(message.chat, user_id, "Member")
        else:
            await bot.decline_chat_join_request(chat_id=chat_id, user_id=user_id)
            await bot.ban_chat_member(chat_id=chat_id, user_id=user_id, until_date=until_ban)
            
            await message.answer(
                f"It's a shame you chose the path of shit... \nYou have one day to turn on your brain and think better before you are unbanned and can enter the chat again.",
                reply_markup=ReplyKeyboardRemove()
            )
            await bot.send_message(
                GROUP,
                f"{link} selected a bullshit term called \"{user_answer}\", so he was banned for one day.",
                parse_mode="HTML"
            )
            
    except Exception as e:
        await message.answer("Error occured. Write @cyber_glor in private.")
    finally:
        if user_id in pending_approvals:
            del pending_approvals[user_id]
