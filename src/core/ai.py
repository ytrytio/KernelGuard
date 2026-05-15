import time
import random
from pathlib import Path
from groq import AsyncGroq
from sys import exit
from logging import getLogger, Logger

from ..config import GROQ_TOKEN, SYSTEM_PROMPT_PATH

logger: Logger = getLogger()

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

    async def ask(
        self,
        previous_ai_text: str,
        current_text: str,
        user_id: int,
        system_prompt: str | None,
	    model: str = "openai/gpt-oss-120b"
    ) -> str | None:
        now = time.time()
        last_time = self.last_request_time.get(user_id, 0)

        if not system_prompt: system_prompt = self.system_prompt

        if now - last_time < self.cooldown:
            return random.choice(self.cooldown_replies)

        self.last_request_time[user_id] = now

        chat_completion = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": previous_ai_text},
                {"role": "user", "content": current_text},
            ],
            model=model,
        )

        try:
            data = chat_completion.model_dump()
        except Exception as e:
            return str(e)

        return chat_completion.choices[0].message.content

if not GROQ_TOKEN:
    logger.critical("GROQ_TOKEN not found in .env")
    exit()

ai = AIHandler(api_key=GROQ_TOKEN)
