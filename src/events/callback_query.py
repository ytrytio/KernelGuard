from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import __version__ as aiogram_version
from asyncio import subprocess, create_subprocess_shell, TimeoutError, wait_for
from pip import __version__ as pip_version
from sys import version as python_version

router = Router(name=__name__)

@router.callback_query(F.data == "ping")
async def ping(callback: CallbackQuery, **kwargs):
    try:
        cmd = "/usr/bin/ping -c 1 api.telegram.org | /usr/bin/awk -F'/' 'END {print $5}'"
        process = await create_subprocess_shell(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await wait_for(process.communicate(), timeout=10.0)

        if process.returncode!= 0:
            raise ValueError(f"Ping command failed: {stderr.decode().strip()}")

        ping_time = stdout.decode().strip()
        if not ping_time:
            raise ValueError("No ping time received")

        await callback.answer(
            f"Pong! \nDelay: {ping_time}ms",
            show_alert=True
        )
    except TimeoutError:
        raise ValueError("Ping timed out")
    except Exception as e:
        await callback.answer(
            f"An error has occurred: {str(e)}",
            show_alert=True
        )

@router.callback_query(F.data == "info")
async def info(callback: CallbackQuery, **kwargs):
    try:
        await callback.answer(
            f"Python: {python_version.split(' ')[0]}\n"
            f"aiogram: {aiogram_version}\n"
            f"pip: {pip_version}",
            show_alert=True
        )
    except Exception as e:
        await callback.answer(
            f"An error has occurred: {str(e)}",
            show_alert=True
        )
