from __future__ import annotations
import os
import httpx
import structlog
from adapters.model_adapter import ModelAdapter

logger = structlog.get_logger()


class OllamaAdapter(ModelAdapter):

    def __init__(self, config: dict):
        # Env var wins — lets docker-compose point to host.docker.internal
        # without changing config/models.json. For pure local dev this just
        # falls through to localhost:11434.
        self.base_url = os.environ.get(
            "OLLAMA_BASE_URL",
            config.get("base_url", "http://localhost:11434"),
        ).rstrip("/")
        self.model       = config.get("model", "llama3")
        self.embed_model = config.get("embed_model", "nomic-embed-text")
        self._client     = httpx.AsyncClient(timeout=120.0)
        logger.info("ollama_adapter.ready", base_url=self.base_url,
                    model=self.model, embed_model=self.embed_model)

    async def generate(self, prompt: str) -> str:
        response = await self._client.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        return response.json().get("response", "")

    async def chat(self, messages: list[dict]) -> str:
        response = await self._client.post(
            f"{self.base_url}/api/chat",
            json={"model": self.model, "messages": messages, "stream": False},
        )
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "")

    async def embed(self, text: str) -> list[float]:
        response = await self._client.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.embed_model, "prompt": text},
        )
        response.raise_for_status()
        return response.json().get("embedding", [])