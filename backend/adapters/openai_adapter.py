from __future__ import annotations
import os
from openai import AsyncOpenAI
from adapters.model_adapter import ModelAdapter
import structlog

logger = structlog.get_logger()


class OpenAIAdapter(ModelAdapter):

    def __init__(self, config: dict):
        """Initialize OpenAI adapter from config dict.
        
        Priority: Environment variables > Config file > Hardcoded defaults
        """
        # API Key
        api_key_env = config.get("api_key_env", "OPENAI_API_KEY")
        api_key = os.environ.get(api_key_env, "")
        
        # API Base
        api_base_env = config.get("api_base_env", "OPENAI_API_BASE")
        api_base_default = config.get("api_base", "https://api.openai.com/v1")
        api_base = os.environ.get(api_base_env, api_base_default)
        
        self.client = AsyncOpenAI(api_key=api_key, base_url=api_base)
        
        # Model resolution
        model_env = config.get("model_env", "OPENAI_MODEL")
        model_default = config.get("model", "gpt-4o")
        self.model = os.environ.get(model_env, model_default)
        
        # Embedding model resolution
        embed_model_env = config.get("embed_model_env", "OPENAI_EMBED_MODEL")
        embed_model_default = config.get("embed_model", "text-embedding-3-small")
        self.embed_model = os.environ.get(embed_model_env, embed_model_default)
        
        # Generation parameters
        self.timeout_seconds = config.get("timeout_seconds", 60)
        self.temperature = config.get("temperature", 0.7)
        self.top_p = config.get("top_p", 1.0)
        self.max_tokens = config.get("max_tokens", 4096)
        
        logger.info("openai_adapter.ready",
                    model=self.model,
                    embed_model=self.embed_model,
                    timeout=self.timeout_seconds)

    async def generate(self, prompt: str) -> str:
        return await self.chat([{"role": "user", "content": prompt}])

    async def chat(self, messages: list[dict]) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            timeout=self.timeout_seconds,
        )
        return response.choices[0].message.content or ""

    async def embed(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model=self.embed_model,
            input=text,
        )
        return response.data[0].embedding