from __future__ import annotations
import os
from openai import AsyncOpenAI
from adapters.model_adapter import ModelAdapter


class OpenAIAdapter(ModelAdapter):

    def __init__(self, config: dict):
        api_key_env      = config.get("api_key_env", "OPENAI_API_KEY")
        self.client      = AsyncOpenAI(api_key=os.environ.get(api_key_env, ""))
        self.model       = config.get("model", "gpt-4o")
        self.embed_model = config.get("embed_model", "text-embedding-3-small")

    async def generate(self, prompt: str) -> str:
        return await self.chat([{"role": "user", "content": prompt}])

    async def chat(self, messages: list[dict]) -> str:
        response = await self.client.chat.completions.create(
            model=self.model, messages=messages,
        )
        return response.choices[0].message.content or ""

    async def embed(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model=self.embed_model, input=text,
        )
        return response.data[0].embedding