from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, LinkPreviewOptions, Message, InlineKeyboardButton
from aiosqlite import Connection
from logging import getLogger, Logger

from ..config import ADMINS, BANNED_MODELS
from ..core.ai import DEFAULT_MODEL, ai
from ..utils.database import database
from ..utils.utils import escape_md_v2_smart

router = Router(name=__name__)
logger: Logger = getLogger()
    
@router.message(F.reply_to_message.from_user.id == F.bot.id)
@database
async def reply_handler(message: Message, db: Connection, bot: Bot, **_):
    if not message.from_user or not message.reply_to_message: 
        return
    
    sender_id = message.from_user.id
    sender_username = message.from_user.username
    tg_name = message.from_user.first_name
    
    user_text = message.text or message.caption or " "
    previous_ai_text = message.reply_to_message.text or " "
    
    if not user_text.strip(): 
        return

    async with db.execute("SELECT name, username, about FROM users WHERE about IS NOT NULL AND about != ''") as cursor:
        all_users = await cursor.fetchall()
    
    known_users = ""
    for row in all_users:
        known_users += f"- {row[0]} (@{row[1]}): {row[2]}\n"

    async with db.execute("SELECT name FROM users WHERE id = ?", (sender_id,)) as cursor:
        user_row = await cursor.fetchone()
        db_name = user_row[0] if user_row else tg_name

    patched_prompt = ai.system_prompt.format(known_users=known_users)
    full_identity = f"{escape_md_v2_smart(tg_name)} ({escape_md_v2_smart(db_name)})"
    
    parsed_user_message = (
        f"{full_identity}\n"
        f"@{sender_username if sender_username else sender_id}\n\n"
        f"{user_text}"
    )

    try:
        model = await ai.get_model()
        clean_text = await ai.ask(
            previous_ai_text=previous_ai_text,
            current_text=parsed_user_message,
            user_id=sender_id,
            system_prompt=patched_prompt,
            model=model
        )
        logger.info("Model: " + model)
        logger.info("Result: " + clean_text)
        if not clean_text.strip():
            clean_text = "Oops, something went wrong."
            
        await message.reply(clean_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"AI error during streaming: {e}")
        await message.reply(f"<blockquote expandable>{e}</blockquote>", link_preview_options=LinkPreviewOptions(is_disabled=True))

@router.message(Command("models"))
async def show_models(message: Message, **_):
    if message.from_user is None: return
    if message.from_user.id not in ADMINS: return await message.reply("Are you sure you have enough rights?")
    
    models = await ai.client.models.list()
    current = await ai.get_model()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{'[ x ]' if current == m.id else '[   ]'} {m.id}", callback_data=f"setmodel:{m.id}", style="danger")]
        for m in models.data 
        if not any(m.id.startswith(word) for word in BANNED_MODELS)
    ])
    await message.reply("Available models:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("setmodel"))
@database
async def select_model(callback: CallbackQuery, db: Connection, **_):
    if not isinstance(callback.message, Message): return
    if callback.from_user.id not in ADMINS: return await callback.answer("Are you sure you have enough rights?", show_alert=True)
    
    chosen = callback.data.split(":")[1] if callback.data else DEFAULT_MODEL
    current = await ai.get_model()
    
    if current == chosen:
        await callback.answer("Already set.", show_alert=True)
    else:
        await db.execute("UPDATE global SET value=? WHERE key=?", (chosen, "model"))
        
        models = await ai.client.models.list()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{'[ x ]' if chosen == m.id else '[   ]'} {m.id}", callback_data=f"setmodel:{m.id}", style="danger")]
            for m in models.data
            if not any(m.id.startswith(word) for word in BANNED_MODELS)
        ])
        await db.commit()
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer(f"Changed to {chosen}.", show_alert=True)
