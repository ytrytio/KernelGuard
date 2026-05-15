from dotenv import dotenv_values
from pathlib import Path

secrets: dict[str, str | None] = dotenv_values(".env")

BOT_TOKEN = secrets.get("BOT_TOKEN", None)
GROQ_TOKEN = secrets.get("GROQ_TOKEN", None)

MARKDOWN_PATTERNS = [
    r'\*[^*]+\*',
    r'_[^_]+_',
    r'__[^_]+__',
    r'~[^~]+~',
    r'\|\|[^|]+\|\|',
    r'`[^`]+`',
    r'\[.+?\]\(.+?\)',
    r'>.*',
]
ESCAPE_CHARS = r'+-={}.!'

ADMINS = [1432248216, -1002500557416, 8081091048, 1069960354]
GROUP = -1002500557416

PROJECT_DIR = Path(__file__).parent.parent
SYSTEM_PROMPT_PATH = PROJECT_DIR / "system_prompt.txt"
DB_PATH = PROJECT_DIR / "data.db"
TEMPLATE_PATH = PROJECT_DIR / "template.sql"
