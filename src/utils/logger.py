import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback

console = Console()

class LogColors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"

def setup_logger(level: int = logging.INFO):
    install_rich_traceback(
        console=console,
        max_frames=4,
        show_locals=False,
        word_wrap=True,
        extra_lines=1,
        suppress=[
            "aiogram.dispatcher",
            "aiogram.fsm",
            "aiogram.event",
            "aiogram.router",
            "aiogram.middlewares",
            "aiogram.utils",
            "asyncio",
            "aiohttp",
        ]
    )

    rich_handler = RichHandler(
        console=console,
        level=level,
        markup=True,
        show_time=True,
        show_level=True,
        show_path=True,
        log_time_format="[%X]",
        rich_tracebacks=True,
        tracebacks_show_locals=False,
        tracebacks_extra_lines=1,
        tracebacks_width=console.width,
        tracebacks_word_wrap=True,
        tracebacks_max_frames=4,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(rich_handler)

    return root_logger
