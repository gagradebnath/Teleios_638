from __future__ import annotations
import os
import anthropic
from adapters.model_adapter import ModelAdapter
import structlog

logger = structlog.get_logger()


class AnthropicAdapter(ModelAdapter):

    def __init__(self, config: dict):
        """Initialize Anthropic adapter from config dict.
        
        Priority: Environment variables > Config file > Hardcoded defaults
        """
        # API Key
        api_key_env = config.get("api_key_env", "ANTHROPIC_API_KEY")
        api_key = os.environ.get(api_key_env, "")
        
        # API Base
        api_base_env = config.get("api_base_env", "ANTHROPIC_API_BASE")
        api_base_default = config.get("api_base", "https://api.anthropic.com")
        api_base = os.environ.get(api_base_env, api_base_default)
        
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        
        # Model resolution
        model_env = config.get("model_env", "ANTHROPIC_MODEL")
        model_default = config.get("model", "claude-sonnet-4-20250514")
        self.model = os.environ.get(model_env, model_default)
        
        # Generation parameters
        self.timeout_seconds = config.get("timeout_seconds", 60)
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 4096)
        
        logger.info("anthropic_adapter.ready",
                    model=self.model,
                    timeout=self.timeout_seconds)

    async def generate(self, prompt: str) -> str:
        return await self.chat([{"role": "user", "content": prompt}])

    async def chat(self, messages: list[dict]) -> str:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=messages,
            timeout=self.timeout_seconds,
        )
        return response.content[0].text if response.content else ""

    async def embed(self, text: str) -> list[float]:
        """Anthropic does not provide embedding API.
        
        Subclasses should override this or use a separate embedding service.
        """
        raise NotImplementedError(
            "Anthropic API does not provide embeddings. "
            "Use a separate embedding service or another provider."
        )
