from aiogram import Bot
from aiogram.enums import ChatType
from aiogram.types import ChatPermissions

from ..config import GROUP

def get_permissions(yet: bool):
    return ChatPermissions(
        can_send_messages=yet,
        can_send_audios=yet,
        can_send_photos=yet,
        can_send_videos=yet,
        can_send_media_messages=yet,
        can_send_video_notes=yet,
        can_send_voice_notes=yet,
        can_send_stickers=yet,
        can_send_animations=yet,
        can_send_games=yet,
        can_use_inline_bots=yet,
        can_add_web_page_previews=yet,
        can_send_polls=yet,
        can_send_other_messages=yet,
        can_react_to_messages=yet,
        can_send_documents=yet,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False
    )

async def change_prefix(bot: Bot, chat_id: int, user_id: int, prefix: str = "Member"):
    await bot.set_chat_member_tag(chat_id, user_id, prefix)
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
