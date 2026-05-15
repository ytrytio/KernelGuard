import sys
from asyncio import run as aiorun
from logging import Logger

from .config import GROUP
from .utils.logger import setup_logger

logger: Logger = setup_logger()

class ImportLogger:
    def find_spec(self, fullname, *_, **__):
        if fullname.startswith(__package__):
            logger.info(f"Loading module: {fullname}")
        return None

sys.meta_path.insert(0, ImportLogger())
logger.info("Initializing system components...")

from .core.bot import bot, dp
from .utils.database import init_db

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    aiorun(main())
