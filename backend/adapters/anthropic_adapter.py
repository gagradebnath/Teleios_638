from __future__ import annotations
import httpx
from adapters.model_adapter import ModelAdapter


class VLLMAdapter(ModelAdapter):

    def __init__(self, config: dict):
        self.base_url = config.get("base_url", "http://localhost:8080").rstrip("/")
        self.model    = config.get("model", "mistralai/Mistral-7B-Instruct-v0.2")
        self._client  = httpx.AsyncClient(timeout=120.0)

    async def generate(self, prompt: str) -> str:
        return await self.chat([{"role": "user", "content": prompt}])

    async def chat(self, messages: list[dict]) -> str:
        response = await self._client.post(
            f"{self.base_url}/v1/chat/completions",
            json={"model": self.model, "messages": messages},
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    async def embed(self, text: str) -> list[float]:
        response = await self._client.post(
            f"{self.base_url}/v1/embeddings",
            json={"model": self.model, "input": text},
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]