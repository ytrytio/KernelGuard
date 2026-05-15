from aiogram import F, Router, Bot
from aiogram.types import ChatJoinRequest, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from ..config import GROUP
from ..storage.temp import pending_approvals

router = Router(name=__name__)

@router.chat_join_request()
async def handle_join_request(request: ChatJoinRequest, bot: Bot):
    user_id = request.from_user.id
    chat_id = request.chat.id
    link = request.from_user.mention_html()
    
    global pending_approvals
    pending_approvals[user_id] = chat_id
    
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Windows")],
            [KeyboardButton(text="Linux")],
            [KeyboardButton(text="MacOS")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    try:
        await request.answer_pm(
            text=f"{link}, welcome to our <s>Gachi Center</s> private Linux community!\n"
           "Please, answer the question below in 30 seconds:\n\n"
           "<i>What OS is the best?</i>", 
            reply_markup=markup,
            parse_mode="HTML"
        )
        await bot.send_animation(
            chat_id=GROUP, 
            animation="CgACAgIAAyEFAASVC3poAAEBjnlpasknV0Q7o-1eUO0LpuynplPWPgACFRgAArcEMUoGJsH6M1CiUjgE",
            caption=f"{link} has sent a request to join. Waiting...",
            parse_mode="HTML"
        )
    except Exception as e:
        raise e
