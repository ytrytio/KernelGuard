import time
import random
import asyncio
from pathlib import Path
from aiosqlite import Connection
from sys import exit
from logging import getLogger, Logger
from llama_cpp import Llama

from ..utils.database import database
from ..config import SYSTEM_PROMPT_PATH, DEFAULT_MODEL

logger: Logger = getLogger()

MODEL_PATH = str(DEFAULT_MODEL)

class AIHandler:
    def __init__(
        self, 
        model_path: str | Path = MODEL_PATH, 
        system_prompt_path: str | Path = SYSTEM_PROMPT_PATH, 
        cooldown: int = 5
    ):
        self.llm = Llama(
            model_path=str(model_path),
            n_ctx=1024,
            n_threads=2,
            verbose=False
        )
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
        return MODEL_PATH

    def _generate_sync(self, messages: list[dict], temperature: float, max_tokens: int) -> str:
        response = self.llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            repeat_penalty=1.22,
            stop=[
                "<|im_end|>", 
                "<|endoftext|>", 
                "\n[",
                "\nUSER:", 
                "\nGLOR:"
            ]
        )
        logger.info(response)
        return response["choices"][0]["message"]["content"] or ""

    async def ask(
        self,
        previous_ai_text: str | None,
        current_text: str,
        user_id: int,
        system_prompt: str | None = None,
        model: str = MODEL_PATH,
        moder: bool = False
    ) -> str:
        if not moder:
            now = time.time()
            last_time = self.last_request_time.get(user_id, 0)
            
            if now - last_time < self.cooldown:
                return random.choice(self.cooldown_replies)
            
            self.last_request_time[user_id] = now
    
        if not system_prompt or not system_prompt.strip():
            system_prompt = self.system_prompt
    
        messages = [{"role": "system", "content": system_prompt.strip()}]
    
        if not moder and previous_ai_text and not previous_ai_text.startswith("Detected violation!"):
            messages.append({"role": "assistant", "content": previous_ai_text.strip()})
    
        messages.append({"role": "user", "content": current_text.strip()})
    
        temperature = 0.1 if moder else 0.7
        max_tokens = 256 if moder else 512
    
        raw_text = await asyncio.to_thread(
            self._generate_sync,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    
        return raw_text.strip()

ai = AIHandler()
