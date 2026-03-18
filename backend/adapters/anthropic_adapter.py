"""
adapters/anthropic_adapter.py — Anthropic Claude adapter.
Note: Anthropic has no public embedding API. embed() raises NotImplementedError.
Do not use AnthropicAdapter as the active provider if embeddings are required
(i.e. when VectorSearchTool or DocumentRetrievalTool need to call adapter.embed).
"""
from __future__ import annotations

import os
from anthropic import AsyncAnthropic
from adapters.model_adapter import ModelAdapter


class AnthropicAdapter(ModelAdapter):

    def __init__(self, config: dict):
        api_key_env = config.get("api_key_env", "ANTHROPIC_API_KEY")
        self.client = AsyncAnthropic(api_key=os.environ.get(api_key_env, ""))
        self.model  = config.get("model", "claude-sonnet-4-20250514")

    async def generate(self, prompt: str) -> str:
        return await self.chat([{"role": "user", "content": prompt}])

    async def chat(self, messages: list[dict]) -> str:
        # Anthropic requires the system message to be separate from the messages list
        system = next(
            (m["content"] for m in messages if m["role"] == "system"),
            None,
        )
        user_messages = [m for m in messages if m["role"] != "system"]

        kwargs: dict = dict(model=self.model, max_tokens=4096, messages=user_messages)
        if system:
            kwargs["system"] = system

        response = await self.client.messages.create(**kwargs)
        return response.content[0].text if response.content else ""

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError(
            "AnthropicAdapter does not support embeddings. "
            "Switch to OllamaAdapter or OpenAIAdapter for vector operations."
        )