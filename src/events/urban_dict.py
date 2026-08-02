from html import escape
from pyurbandict import UrbanDict

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

router = Router(name=__name__)
commands = ["ud", "urban", "whatis"]


@router.message(Command(commands=commands))
async def urban_dict(message: Message, command: CommandObject):
    query = command.args

    if not query:
        aliases = "|".join(commands)
        await message.reply(
            "```text\nUsage:\n" f"  /{{{aliases}}} <query>\n" "```",
            parse_mode="Markdown",
        )
        return

    word = UrbanDict(query)
    results = word.search()

    if not results:
        await message.reply("Definition not found.")
        return

    result = results[0]

    blocks = [
        f"<blockquote expandable><b>Query</b>\n<i>{escape(query)}</i></blockquote>",
        f"<blockquote expandable><b>Definition</b>\n<i>{escape(result.definition or '')}</i></blockquote>",
    ]

    if result.example:
        blocks.append(f"<blockquote expandable><b>Example</b>\n<i>{escape(result.example)}</i></blockquote>")

    if result.author:
        blocks.append(f"<blockquote><b>Author</b>\n<i>{escape(result.author)}</i></blockquote>")

    blocks.append(f"\n<i>👍 {result.thumbs_up or 0} </i>|<i> 👎 {result.thumbs_down or 0}</i>")

    text = "\n".join(blocks)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Link", url=result.permalink)]
        ]
    )

    await message.reply(text, parse_mode="HTML", reply_markup=kb)
