from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiosqlite import Connection
from html import escape
from platform import release

from ..utils.database import database
from ..utils.utils import get_human_uptime

router = Router(name=__name__)

async def check_user(db: Connection, user_id: int, full_name: str, username: str | None = None):
    async with db.execute("SELECT username FROM users WHERE id=?", (user_id,)) as cursor:
        user = await cursor.fetchone()
        
    if not user:
        await db.execute(
            "INSERT INTO users (id, name, username) VALUES (?, ?, ?)",
            (user_id, escape(full_name[:25]), username)
        )
        await db.commit()
    else:
        current_username = user[0]
        if current_username != username:
            await db.execute(
                "UPDATE users SET username=? WHERE id=?",
                (username, user_id)
            )
            await db.commit()

@router.message(Command("name"))
@database
async def name(message: Message, db: Connection, command: CommandObject, bot: Bot):
    if not message.from_user: return

    await check_user(
        db, 
        message.from_user.id, 
        message.from_user.full_name, 
        message.from_user.username
    )
    
    new_name = command.args

    if not new_name:
        await message.reply(
            "```bash\n"
            "Usage\n"
            "  /name <text>"
            "```",
            parse_mode = "markdown"
        )
        return
    
    if len(new_name) > 25:
        await message.reply("Too long name (>25), try again with another one.")
        return
        
    await db.execute("UPDATE users SET name=? WHERE id=?", (escape(new_name), message.from_user.id))
    await db.commit()
    await message.reply(f"Your name has been successfully changed to <b>{escape(new_name)}</b>.")

@router.message(Command("about"))
@database
async def about(message: Message, db: Connection, command: CommandObject, bot: Bot):
    if not message.from_user: return
    
    await check_user(
        db, 
        message.from_user.id, 
        message.from_user.full_name, 
        message.from_user.username
    )
    
    about = command.args
    
    if not about:
        await message.reply(
            "```bash\n"
            "Usage\n"
            "  /about <text>"
            "```",
            parse_mode = "markdown"
        )
        return
    
    if len(about) > 200:
        await message.reply("Too long description (>200), try again with another one.")
        return
        
    await db.execute("UPDATE users SET about=? WHERE id=?", (escape(about), message.from_user.id))
    await db.commit()
    await message.reply(f"Your description has been successfully changed.")

@router.message(Command(commands=["me", "fetch", "info"]))
@database
async def me(message: Message, db: Connection, bot: Bot):
    if not message.from_user: return
    
    await check_user(
        db, 
        message.from_user.id, 
        message.from_user.full_name, 
        message.from_user.username
    )

    query = await db.execute("SELECT name, about, created_at FROM users WHERE id=?", (message.from_user.id,))
    data = await query.fetchone()

    if not data: return

    name = data["name"]
    about = data["about"]
    uptime = data["created_at"]
    username = message.from_user.username or "user"

    await message.reply(
        "```bash\n"
        f"{username}@kernelguard\n"
        f"Host: {name}\n"
        f"Kernel: {release()}\n"
        f"Uptime: {get_human_uptime(uptime)}\n"
        f"About: {about}\n"
        "```",
        parse_mode = "markdown"
    )
