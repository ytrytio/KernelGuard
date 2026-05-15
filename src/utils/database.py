from typing import Callable, Any, Awaitable
from typing_extensions import Callable
from aiosqlite import connect, Row, Connection
from aiofiles import open as aiopen
from functools import wraps

from ..config import DB_PATH, TEMPLATE_PATH

def database(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if "db" in kwargs and kwargs["db"] is not None:
            return await func(*args, **kwargs)
        async with connect(DB_PATH) as db:
            db.row_factory = Row
            kwargs["db"] = db
            return await func(*args, **kwargs)
    return wrapper

@database
async def init_db(db: Connection):
    if not TEMPLATE_PATH.exists(): raise FileNotFoundError(f"{TEMPLATE_PATH} not found.")
    async with aiopen(TEMPLATE_PATH, "r", encoding="utf-8") as f: sql_script = await f.read()
    await db.executescript(sql_script)
    await db.commit()
