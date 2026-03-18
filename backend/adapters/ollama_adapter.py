from __future__ import annotations
import os
import httpx
import structlog
from adapters.model_adapter import ModelAdapter

logger = structlog.get_logger()


class OllamaAdapter(ModelAdapter):

    def __init__(self, config: dict):
        """Initialize Ollama adapter from config dict.
        
        Priority: Environment variables > Config file > Hardcoded defaults
        """
        # Base URL resolution
        base_url_env = config.get("base_url_env", "OLLAMA_BASE_URL")
        base_url_default = config.get("base_url", "http://localhost:11434")
        self.base_url = os.environ.get(base_url_env, base_url_default).rstrip("/")
        
        # Model resolution
        model_env = config.get("model_env", "OLLAMA_MODEL")
        model_default = config.get("model", "qwen2.5-coder:3b")
        self.model = os.environ.get(model_env, model_default)
        
        # Embedding model resolution
        embed_model_env = config.get("embed_model_env", "OLLAMA_EMBEDDING_MODEL")
        embed_model_default = config.get("embed_model", "nomic-embed-text")
        self.embed_model = os.environ.get(embed_model_env, embed_model_default)
        
        # Timeout
        self.timeout_seconds = config.get("timeout_seconds", 120)
        
        # Generation parameters
        self.temperature = config.get("temperature", 0.7)
        self.top_p = config.get("top_p", 0.9)
        
        self._client = httpx.AsyncClient(timeout=self.timeout_seconds)
        
        logger.info("ollama_adapter.ready", 
                    base_url=self.base_url,
                    model=self.model, 
                    embed_model=self.embed_model,
                    timeout=self.timeout_seconds)

    async def generate(self, prompt: str) -> str:
        response = await self._client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model, 
                "prompt": prompt, 
                "stream": False,
                "temperature": self.temperature,
                "top_p": self.top_p,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json().get("response", "")

    async def chat(self, messages: list[dict]) -> str:
        response = await self._client.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model, 
                "messages": messages, 
                "stream": False,
                "temperature": self.temperature,
                "top_p": self.top_p,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "")

    async def embed(self, text: str) -> list[float]:
        response = await self._client.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.embed_model, "prompt": text},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json().get("embedding", [])
