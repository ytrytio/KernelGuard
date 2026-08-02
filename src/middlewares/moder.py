import json
import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ReactionTypeEmoji, TelegramObject

from ..config import ADMINS, RULES_PROMPT_PATH, GROUP
# from ..core.ai import ai

logger = logging.getLogger(__name__)

# class ContentModeratorMiddleware(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any]
#     ) -> Any:
#         if not isinstance(event, Message) or not event.bot or not event.from_user: return await handler(event, data)
#         if not event.text or event.chat.type not in ["group", "supergroup"] or event.from_user.id in ADMINS:
#             return await handler(event, data)
#             
#         ai_response_text = ""
#         
#         try: 
#             ai_response_text = await ai.ask(
#                 previous_ai_text=None,
#                 current_text=event.text,
#                 user_id=event.from_user.id,
#                 system_prompt=ai._load_prompt(RULES_PROMPT_PATH),
#                 model="openai/gpt-oss-safeguard-20b",
#                 moder=True
#             )
#             
#             result = json.loads(ai_response_text)
#             
#             if result.get("is_violation"):
#                 reason = result.get("reason", "Нарушение правил сообщества")
#                 
#                 await event.react(reaction=[ReactionTypeEmoji(emoji="🖕")])
#                 
#                 for admin in ADMINS:
#                     await event.bot.send_message(
#                         admin,
#                         f"Detected violation! \nReason: {reason}",
#                         disable_notification=True,
#                         reply_markup=InlineKeyboardMarkup(
#                             inline_keyboard=[
#                                 [InlineKeyboardButton(text="Check out", url=f"https://t.me/c/{str(GROUP).replace('-100', '')}/{event.message_id}")]
#                             ]
#                         )
#                     )
#                 
#                 logger.info(f"AI Moderator: Detected violation from {event.from_user.id}. \nMessage: {event.text}\nReason: {reason}")
#                 return
#                 
#         except json.JSONDecodeError:
#             logger.error(f"AI Moderator: Failed to parse JSON from AI. Response: {ai_response_text}")
#         except Exception as e:
#             logger.error(f"AI Moderator: Error: {e}")
# 
#         return await handler(event, data)
