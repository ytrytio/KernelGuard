from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from sys import exit
from logging import getLogger, Logger

from ..events import get_all_routers
from ..config import BOT_TOKEN
from ..middlewares.moder import ContentModeratorMiddleware

logger: Logger = getLogger()

if not BOT_TOKEN:
    logger.critical("BOT_TOKEN not found in .env")
    exit()

bot: Bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode="HTML"
    )
)

dp: Dispatcher = Dispatcher()
dp.include_routers(*get_all_routers())
dp.message.outer_middleware(ContentModeratorMiddleware())
