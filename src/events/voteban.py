from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiosqlite import Connection
from asyncio import Task, create_task, sleep
from typing import Coroutine

from ..utils.database import database
from ..utils.helpers import check, get_permissions, is_admin
from ..utils.members import can_vote
from ..config import GROUP, VOTEBAN_VOTING_HOURS, VOTEBAN_TIEBREAK_HOURS, VOTEBAN_GRACE_HOURS

router = Router(name=__name__)

timers: set[Task] = set()

def link_to(message_id: int) -> str:
    return f"https://t.me/c/{str(GROUP).replace('-100', '', 1)}/{message_id}"

TIE_TEXT = f"Tie. Voting extended by {VOTEBAN_TIEBREAK_HOURS} hour."
MUTED_TEXT = "Target is muted until the end of voting."

def spawn(coroutine: Coroutine):
    task = create_task(coroutine)
    timers.add(task)
    task.add_done_callback(timers.discard)

def keyboard(voteban_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Yes", callback_data=f"vb:{voteban_id}:1"),
        InlineKeyboardButton(text="No", callback_data=f"vb:{voteban_id}:0")
    ]])

def render(target_link: str, initiator_link: str, yes: int, no: int, notes: list[str]) -> str:
    text = f"Voteban: {target_link}\nStarted by {initiator_link}\nYes: {yes}, No: {no}"
    return "\n\n".join([text, *notes]) if notes else text

async def tally(db: Connection, voteban_id: int) -> tuple[int, int]:
    async with db.execute(
        "SELECT COALESCE(SUM(vote = 1), 0), COALESCE(SUM(vote = 0), 0) FROM voteban_votes WHERE voteban_id = ?",
        (voteban_id,)
    ) as cursor:
        row = await cursor.fetchone()
    return row[0], row[1]

async def update(bot: Bot, db: Connection, voteban_id: int, result: str | None = None):
    async with db.execute(
        "SELECT chat_id, message_id, target_link, initiator_link, extended, muted FROM votebans WHERE id = ?",
        (voteban_id,)
    ) as cursor:
        chat_id, message_id, target_link, initiator_link, extended, muted = await cursor.fetchone()

    yes, no = await tally(db, voteban_id)
    if result:
        notes = [result]
    else:
        notes = [text for text, active in ((TIE_TEXT, extended), (MUTED_TEXT, muted)) if active]

    await bot.edit_message_text(
        render(target_link, initiator_link, yes, no, notes),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=None if result else keyboard(voteban_id),
        parse_mode="HTML"
    )

@database
async def finish(bot: Bot, voteban_id: int, db: Connection):
    async with db.execute(
        "SELECT target_id, extended, muted FROM votebans WHERE id = ?",
        (voteban_id,)
    ) as cursor:
        target_id, extended, muted = await cursor.fetchone()

    yes, no = await tally(db, voteban_id)

    if yes == no and not extended:
        await db.execute("UPDATE votebans SET extended = 1 WHERE id = ?", (voteban_id,))
        await db.commit()
        await update(bot, db, voteban_id)
        return spawn(finish_after(bot, voteban_id, VOTEBAN_TIEBREAK_HOURS * 3600))

    await db.execute("UPDATE votebans SET closed = 1 WHERE id = ?", (voteban_id,))
    await db.commit()

    if yes > no:
        await bot.ban_chat_member(GROUP, user_id=target_id)
        result = "Banned."
    else:
        if muted:
            await bot.restrict_chat_member(GROUP, user_id=target_id, permissions=get_permissions(True))
        result = "Not banned."

    await update(bot, db, voteban_id, result)

async def finish_after(bot: Bot, voteban_id: int, delay: float):
    await sleep(delay)
    await finish(bot, voteban_id)

@database
async def mute_delay(voteban_id: int, db: Connection) -> float | None:
    async with db.execute(
        "SELECT closed, muted, CAST((julianday(mute_at) - julianday('now')) * 86400 AS INTEGER) "
        "FROM votebans WHERE id = ?",
        (voteban_id,)
    ) as cursor:
        closed, muted, delay = await cursor.fetchone()
    return None if closed or muted else delay

@database
async def mute(bot: Bot, voteban_id: int, db: Connection):
    async with db.execute("SELECT target_id, closed FROM votebans WHERE id = ?", (voteban_id,)) as cursor:
        target_id, closed = await cursor.fetchone()
    if closed: return

    await bot.restrict_chat_member(GROUP, user_id=target_id, permissions=get_permissions(False))
    await db.execute("UPDATE votebans SET muted = 1 WHERE id = ?", (voteban_id,))
    await db.commit()
    await update(bot, db, voteban_id)

async def mute_after(bot: Bot, voteban_id: int):
    while (delay := await mute_delay(voteban_id)) is not None:
        if delay <= 0: return await mute(bot, voteban_id)
        await sleep(delay)

@router.startup()
@database
async def resume(bot: Bot, db: Connection):
    async with db.execute(
        "SELECT id, muted, CAST((julianday(created_at, '+' || (? + extended * ?) || ' hours') - julianday('now')) * 86400 AS INTEGER) "
        "FROM votebans WHERE closed = 0",
        (VOTEBAN_VOTING_HOURS, VOTEBAN_TIEBREAK_HOURS)
    ) as cursor:
        rows = await cursor.fetchall()
    for voteban_id, muted, remaining in rows:
        spawn(finish_after(bot, voteban_id, max(remaining, 0)))
        if not muted: spawn(mute_after(bot, voteban_id))

@router.message(Command("voteban"))
@database
async def voteban(message: Message, bot: Bot, db: Connection):
    if not message.reply_to_message: return await message.reply("Try writing in reply to a message.")
    if message.from_user is None or message.reply_to_message.from_user is None: return

    chat_id = message.chat.id
    chat_type = message.chat.type
    user_id = message.from_user.id
    victim = message.reply_to_message.from_user

    if not await check(chat_type, chat_id, message): return
    if not await can_vote(bot, db, user_id): return await message.reply("You can not start a voteban yet.")
    if victim.is_bot or victim.id == user_id or await is_admin(bot, victim.id):
        return await message.reply("This user can not be voted against.")

    async with db.execute("SELECT message_id FROM votebans WHERE target_id = ? AND closed = 0", (victim.id,)) as cursor:
        existing = await cursor.fetchone()
    if existing:
        return await message.reply(
            f'A voteban against this user <a href="{link_to(existing[0])}">already exists</a>.',
            parse_mode="HTML"
        )

    target_link = victim.mention_html()
    initiator_link = message.from_user.mention_html()
    cursor = await db.execute(
        "INSERT INTO votebans (chat_id, target_id, target_link, initiator_link, mute_at) "
        "VALUES (?, ?, ?, ?, DATETIME('now', ?))",
        (GROUP, victim.id, target_link, initiator_link, f"+{VOTEBAN_GRACE_HOURS} hours")
    )
    voteban_id = cursor.lastrowid
    await db.commit()

    sent = await bot.send_message(
        GROUP,
        render(target_link, initiator_link, 0, 0, []),
        reply_markup=keyboard(voteban_id),
        parse_mode="HTML"
    )
    await db.execute("UPDATE votebans SET message_id = ? WHERE id = ?", (sent.message_id, voteban_id))
    await db.commit()

    spawn(finish_after(bot, voteban_id, VOTEBAN_VOTING_HOURS * 3600))
    spawn(mute_after(bot, voteban_id))

@router.message(Command("postpone"))
@database
async def postpone(message: Message, bot: Bot, db: Connection):
    if not message.reply_to_message: return await message.reply("Try writing in reply to a message.")
    if message.from_user is None: return
    if not await is_admin(bot, message.from_user.id): return await message.reply("Are you sure you have enough rights?")

    async with db.execute(
        "SELECT id, muted FROM votebans WHERE chat_id = ? AND message_id = ? AND closed = 0",
        (message.chat.id, message.reply_to_message.message_id)
    ) as cursor:
        row = await cursor.fetchone()

    if row is None: return await message.reply("Voteban not found.")
    if row[1]: return await message.reply("Target is already muted.")

    await db.execute(
        "UPDATE votebans SET mute_at = DATETIME(mute_at, ?) WHERE id = ?",
        (f"+{VOTEBAN_GRACE_HOURS} hours", row[0])
    )
    await db.commit()
    await message.reply(f"Mute postponed by {VOTEBAN_GRACE_HOURS} hour.")

@router.callback_query(F.data.startswith("vb:"))
@database
async def vote(callback: CallbackQuery, bot: Bot, db: Connection):
    if callback.data is None: return

    _, raw_id, raw_vote = callback.data.split(":")
    voteban_id = int(raw_id)
    voter_id = callback.from_user.id

    async with db.execute("SELECT closed, target_id FROM votebans WHERE id = ?", (voteban_id,)) as cursor:
        row = await cursor.fetchone()

    if row is None or row[0]: return await callback.answer("Voting is closed.", show_alert=True)
    if voter_id == row[1]: return await callback.answer("You can not vote in your own voteban.", show_alert=True)
    if not await can_vote(bot, db, voter_id): return await callback.answer("You can not vote yet.", show_alert=True)

    cursor = await db.execute(
        "INSERT OR IGNORE INTO voteban_votes (voteban_id, voter_id, vote) VALUES (?, ?, ?)",
        (voteban_id, voter_id, int(raw_vote))
    )
    await db.commit()
    if cursor.rowcount == 0: return await callback.answer("You have already voted.")

    await update(bot, db, voteban_id)
    await callback.answer("Vote counted.")
