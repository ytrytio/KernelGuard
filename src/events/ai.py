from aiogram import F, Router
from aiogram.types import Message
from aiosqlite import Connection
from logging import getLogger, Logger

from ..core.ai import ai
from ..utils.database import database
from ..utils.utils import escape_md_v2_smart

router = Router(name=__name__)
logger: Logger = getLogger()
    
@router.message(F.reply_to_message.from_user.id == F.bot.id)
@database
async def reply_handler(message: Message, db: Connection, **_):
    if not message.from_user or not message.reply_to_message: return
    
    sender_id = message.from_user.id
    sender_username = message.from_user.username
    tg_name = message.from_user.first_name
    
    user_text = message.text or message.caption or " "
    previous_ai_text = message.reply_to_message.text or " "
    
    if not user_text.strip(): return

    async with db.execute("SELECT name, username, about FROM users WHERE about IS NOT NULL AND about != ''") as cursor:
        all_users = await cursor.fetchall()
    
    known_users = ""
    for row in all_users:
        known_users += f"- {row[0]} (@{row[1]}): {row[2]}\n"

    async with db.execute("SELECT name FROM users WHERE id = ?", (sender_id,)) as cursor:
        user_row = await cursor.fetchone()
        db_name = user_row[0] if user_row else tg_name

    patched_prompt = ai.system_prompt.format(known_users)

    full_identity = f"{escape_md_v2_smart(tg_name)} ({escape_md_v2_smart(db_name)})"
    
    parsed_user_message = (
        f"{full_identity}\n"
        f"@{sender_username if sender_username else sender_id}\n\n"
        f"{user_text}"
    )

    try:
        reply_text = await ai.ask(
            previous_ai_text,
            parsed_user_message,
            sender_id,
            patched_prompt
        )
        await message.reply(reply_text or "Oops, something went wrong.", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"AI error: {e}")
