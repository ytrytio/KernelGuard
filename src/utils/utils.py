from re import sub, escape, DOTALL, IGNORECASE, MULTILINE
from datetime import datetime

from ..config import MARKDOWN_PATTERNS, ESCAPE_CHARS

def clean_think(text: str) -> str:
    cleaned_text = sub(r'<think>.*?</think>', '', text, flags=DOTALL | IGNORECASE)
    return cleaned_text.strip()

def escape_md_v2_smart(text: str) -> str:
    placeholders = {}

    def repl(match):
        key = f"__PLACEHOLDER_{len(placeholders)}__"
        placeholders[key] = match.group(0)
        return key

    for pattern in MARKDOWN_PATTERNS:
        text = sub(pattern, repl, text, flags=MULTILINE)

    text = sub(f'([{escape(ESCAPE_CHARS)}])', r'\\\1', text)

    for key, val in placeholders.items():
        text = text.replace(key, val)

    return text

def get_human_uptime(created_at_str: str) -> str:
    try:
        dt_created = datetime.strptime(created_at_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
        diff = datetime.now() - dt_created
        
        days = diff.days
        seconds = diff.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        parts = []
        if days > 0: parts.append(f"{days} days")
        if hours > 0: parts.append(f"{hours} hours")
        if minutes > 0: parts.append(f"{minutes} mins")
        
        return ", ".join(parts) if parts else "just joined"
    except Exception:
        return "unknown"
