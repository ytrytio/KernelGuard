from asyncio import sleep as asleep

from aiogram.enums import ChatType
from aiogram.types import ChatPermissions

from ..config import GROUP

def get_permissions(yet: bool):
    return ChatPermissions(
        can_send_messages=yet,
        can_send_media_messages=yet,
        can_send_stickers=yet,
        can_send_animations=yet,
        can_send_games=yet,
        can_use_inline_bots=yet,
        can_add_web_page_previews=yet,
        can_send_polls=yet,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False
    )

async def change_prefix(bot, chat, user_id, prefix="Member"):
    await chat.promote(
        user_id=user_id,
        can_change_info=False,
        can_delete_messages=False,
        can_delete_stories=False,
        can_edit_messages=False,
        can_edit_stories=False,
        can_invite_users=False,
        can_manage_chat=False,
        can_manage_video_chats=False,
        can_pin_messages=False,
        can_post_messages=False,
        can_post_stories=True,
        can_promote_members=False,
        can_restrict_members=False,
        is_anonymous=False
    )
    await asleep(5)
    await bot.set_chat_administrator_custom_title(chat.id, user_id, prefix)
    return

async def check(chat_type, chat_id, message):
    if chat_type != ChatType.PRIVATE and chat_id != GROUP:
        await message.answer(
            "<b><i>"
            "———————|  A L E R T  |———————\n\n"
            "[*] SYSTEM ANALYSIS COMPLETE [*]\n"
            "GROUP NOT REGISTERED IN WHITELIST.\n"
            "——————————————————————\n"
            "SELF-TERMINATION PROTOCOL ENGAGED."
            "</i></b>",
            parse_mode="HTML"
        )
        await message.chat.leave()
        return False
    else:
        return True
