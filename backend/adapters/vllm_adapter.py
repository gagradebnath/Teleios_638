from __future__ import annotations
import os
import httpx
import structlog
from adapters.model_adapter import ModelAdapter

logger = structlog.get_logger()


class VLLMAdapter(ModelAdapter):

    def __init__(self, config: dict):
        """Initialize VLLM adapter from config dict.
        
        Priority: Environment variables > Config file > Hardcoded defaults
        """
        # Base URL resolution
        base_url_env = config.get("base_url_env", "VLLM_BASE_URL")
        base_url_default = config.get("base_url", "http://localhost:8080")
        self.base_url = os.environ.get(base_url_env, base_url_default).rstrip("/")
        
        # Model resolution
        model_default = config.get("model", "mistralai/Mistral-7B-Instruct-v0.2")
        self.model = model_default
        
        # Timeout
        self.timeout_seconds = config.get("timeout_seconds", 120)
        
        # Generation parameters
        self.temperature = config.get("temperature", 0.7)
        self.top_p = config.get("top_p", 0.9)
        
        self._client = httpx.AsyncClient(timeout=self.timeout_seconds)
        
        logger.info("vllm_adapter.ready",
                    base_url=self.base_url,
                    model=self.model,
                    timeout=self.timeout_seconds)

    async def generate(self, prompt: str) -> str:
        return await self.chat([{"role": "user", "content": prompt}])

    async def chat(self, messages: list[dict]) -> str:
        response = await self._client.post(
            f"{self.base_url}/v1/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "top_p": self.top_p,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    async def embed(self, text: str) -> list[float]:
        response = await self._client.post(
            f"{self.base_url}/v1/embeddings",
            json={"model": self.model, "input": text},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
