from aiogram import Router

from ..config import GROUP

router = Router(name=__name__)

@router.startup()
async def startup():
    from ..core.bot import bot
    await bot.send_message(GROUP, "<i>You've awakened the most ardent defender of free software...</i>")
