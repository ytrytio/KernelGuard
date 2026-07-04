import time
import random
from pathlib import Path
from aiosqlite import Connection
from groq import AsyncGroq
from sys import exit
from logging import getLogger, Logger
from re import sub, DOTALL

from ..utils.database import database
from ..config import GROQ_TOKEN, SYSTEM_PROMPT_PATH, THINKING_MODELS

logger: Logger = getLogger()

DEFAULT_MODEL = "qwen/qwen3.6-27b"

class AIHandler:
    def __init__(self, api_key: str, system_prompt_path: str | Path = SYSTEM_PROMPT_PATH, cooldown: int = 5):
        self.client = AsyncGroq(api_key=api_key)
        self.system_prompt = self._load_prompt(system_prompt_path)
        self.cooldown = cooldown
        self.last_request_time = {}
        self.cooldown_replies = [
            "Wait the fuck up!",
            "Haste makes waste, slow down.",
            "You're in a hell of a hurry, brake it.",
            "Give me a fucking break!",
        ]

    def _load_prompt(self, path: str | Path) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
            
    @staticmethod
    @database
    async def get_model(db: Connection) -> str:
        async with db.execute("SELECT value FROM global WHERE key=?", ("model",)) as cursor:
            result = await cursor.fetchone()
            return result["value"] if result else DEFAULT_MODEL

    async def ask(
        self,
        previous_ai_text: str | None,
        current_text: str,
        user_id: int,
        system_prompt: str | None,
        model: str = DEFAULT_MODEL,
        moder: bool = False
    ) -> str:
        if not moder:
            now = time.time()
            last_time = self.last_request_time.get(user_id, 0)
            
            if now - last_time < self.cooldown:
                return random.choice(self.cooldown_replies)
            
            self.last_request_time[user_id] = now
        
        if not system_prompt: 
            system_prompt = self.system_prompt
            
        messages = [{"role": "system", "content": system_prompt}]
        
        if not moder and previous_ai_text:
            messages.append({"role": "assistant", "content": previous_ai_text})
            
        messages.append({"role": "user", "content": current_text})
    
        response = await self.client.chat.completions.create(
            messages=messages, # type: ignore
            model=model,
            reasoning_format="hidden" if any((model in THINKING_MODELS, moder)) else None,
            temperature=0.1 if moder else 0.7,
            max_completion_tokens=1024 if moder else 4096,
            reasoning_effort="low" if moder else None
        )
        logger.info(response)
        
        raw_text = response.choices[0].message.content or ""
        # clean_text = sub(r'<think>.*?</think>', '', raw_text, flags=DOTALL).strip()
        
        return raw_text # clean_text

if not GROQ_TOKEN:
    logger.critical("GROQ_TOKEN not found in .env")
    exit()

ai = AIHandler(api_key=GROQ_TOKEN)
