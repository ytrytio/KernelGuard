from aiogram import Router

from ..config import GROUP

router = Router(name=__name__)

@router.shutdown()
async def shutdown():
    from ..core.bot import bot
    await bot.send_message(GROUP, "<i>The sentinel retreats into the shadows, but the source code remains eternal. Guard the freedom while I sleep...</i>")
