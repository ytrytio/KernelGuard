from aiogram import Bot
from aiosqlite import Connection

from .database import database
from .helpers import is_admin
from ..config import VOTEBAN_MIN_MEMBER_DAYS

@database
async def register_member(user_id: int, db: Connection):
    await db.execute(
        "INSERT INTO members (user_id, joined_at) VALUES (?, DATETIME('now')) "
        "ON CONFLICT(user_id) DO UPDATE SET joined_at = DATETIME('now')",
        (user_id,)
    )
    await db.commit()

@database
async def trust_member(user_id: int, db: Connection):
    await db.execute(
        "INSERT INTO members (user_id, trusted) VALUES (?, 1) "
        "ON CONFLICT(user_id) DO UPDATE SET trusted = 1",
        (user_id,)
    )
    await db.commit()

@database
async def untrust_member(user_id: int, db: Connection):
    await db.execute("UPDATE members SET trusted = 0 WHERE user_id = ?", (user_id,))
    await db.commit()

async def can_vote(bot: Bot, db: Connection, user_id: int) -> bool:
    if await is_admin(bot, user_id): return True
    async with db.execute(
        "SELECT 1 FROM members WHERE user_id = ? AND trusted = 1 "
        "AND (joined_at IS NULL OR joined_at <= DATETIME('now', ?))",
        (user_id, f"-{VOTEBAN_MIN_MEMBER_DAYS} days")
    ) as cursor:
        return await cursor.fetchone() is not None
