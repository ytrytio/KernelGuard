from aiogram import F, Router, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from ..utils.helpers import check

router = Router(name=__name__)

@router.message(Command("echo"))
async def echo(message: Message):
    if message.text is None: return
    parts = message.text.split()

    if len(parts) < 2:
        await message.reply(
            "```bash\n"
            "Usage\n"
            "  /echo [options] <text>\n\n"
            "Options:\n"
            "  <text>    Text to repeat\n"
            "  -d        Delete /echo message\n"
            "  -h        Enable HTML parsing\n"
            "  -m        Enable Markdown parsing\n"
            "  -f        Repeat the entire message\n"
            "  -r        Reply to a replied message\n"
            "```",
            parse_mode = "markdown"
        )
        return

    args = parts[1] if len(parts) > 1 and parts[1].startswith('-') else None
    text_parts = parts[2:] if args else parts[1:]

    if not text_parts:
        await message.reply(
            "```bash\n"
            "Usage\n"
            "  /echo [options] <text>\n\n"
            "Options:\n"
            "  <text>    Text to repeat\n"
            "  -d        Delete /echo message\n"
            "  -h        Enable HTML parsing\n"
            "  -m        Enable Markdown parsing\n"
            "  -f        Repeat the entire message\n"
            "  -r        Reply to a replied message\n"
            "```",
            parse_mode = "markdown",
            allow_sending_without_reply=True
        )
        return

    text = " ".join(text_parts) if text_parts else ""
    parse_mode = None
    msg = message
    msg_id = None
    delete = False

    if args:
        if 'h' in args: parse_mode = "HTML"
        elif 'm' in args: parse_mode = "Markdown"
        if 'f' in args: text = message.text
        if 'r' in args:
            msg_id = message.reply_to_message.message_id if message.reply_to_message else message.message_id
            msg = message.reply_to_message if message.reply_to_message else message
        if 'd' in args: delete = True

    try:
        await msg.reply(
            text=text,
            parse_mode=parse_mode,
            allow_sending_without_reply=True,
            disable_web_page_preview=True
        )
        if delete: await message.delete()
    except Exception as e:
        await message.reply(
            f"An error occured: {e}",
            allow_sending_without_reply=True
        )


@router.message(Command("start"))
async def start(message: Message):
    if message.from_user is None: return
    chat_id = message.chat.id
    chat_type = message.chat.type

    if not await check(chat_type, chat_id, message): return
    else:
        await message.reply(
            "Sup, what you need?",
            allow_sending_without_reply=True,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Ping", callback_data="ping")],
                    [InlineKeyboardButton(text="Info", callback_data="info")],
                ]
            )
        )
