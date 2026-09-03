from aiogram import Bot, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiosqlite import Connection

from ..utils.database import database
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

@router.message(Command("ping"))
@database
async def everyone(message: Message, db: Connection):
    if message.from_user is None:
        return

    chat_id = message.chat.id
    chat_type = message.chat.type
    user_id = message.from_user.id

    if user_id not in ADMINS:
        return await message.reply("Are you sure you have enough rights?")
    if not await check(chat_type, chat_id, message):
        return

    parts = message.text.split() if message.text else []
    args = parts[1] if len(parts) > 1 and parts[1].startswith("-") else None

    if args and "h" in args:
        return await message.reply(
            "```bash\n"
            "Usage:\n"
            "  /ping [options]\n\n"
            "Options:\n"
            "  -q        Quiet output (hide host list and tag invisibly)\n"
            "  -h        Print help and exit\n"
            "```",
            parse_mode="markdown",
        )

    query = await db.execute("SELECT id, username FROM users")
    users = list(await query.fetchall())

    if not users: return await message.reply("No users found.")

    quiet = "q" in args if args else False
    hidden_char = chr(0x206C)

    total_hosts = len(users)
    received_hosts = 0

    mentions = []
    hidden_tags = []

    for user_item in users:
        u_id, username = user_item[0], user_item[1]

        hidden_tags.append(f"[{hidden_char}](tg://user?id={u_id})")

        if username:
            received_hosts += 1
            if not quiet:
                mentions.append(f"64 bytes from @{username}: icmp_seq=1 ttl=64 time=0.0 ms")

    loss_percent = int(
        ((total_hosts - received_hosts) / total_hosts) * 100
    ) if total_hosts > 0 else 0

    hidden_payload = "".join(hidden_tags)

    if quiet:
        ping_text = (
            "```bash\n"
            "PING everyone (kernelsyndicate) 56(84) bytes of data.\n"
            "--- everyone ping statistics ---\n"
            f"{total_hosts} packets transmitted, {received_hosts} received, {loss_percent}% packet loss\n"
            "```"
            f"{hidden_payload}"
        )
    else:
        users_str = "\n".join(mentions) if mentions else "None"
        ping_text = (
            "```bash\n"
            "PING everyone (kernelsyndicate) 56(84) bytes of data.\n"
            f"{users_str}"
            "\n--- everyone ping statistics ---\n"
            f"{total_hosts} packets transmitted, {received_hosts} received, {loss_percent}% packet loss\n"
            "```"
            f"{hidden_payload}"
        )

    try:
        await message.reply(
            ping_text,
            parse_mode="markdown",
            allow_sending_without_reply=True,
        )
    except Exception as e:
        await message.reply(
            f"An error occured: {e}",
            allow_sending_without_reply=True,
        )
