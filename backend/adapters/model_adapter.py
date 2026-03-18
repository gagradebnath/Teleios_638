"""
adapters/model_adapter.py — Abstract ModelAdapter interface.

Every provider adapter must implement generate, chat, and embed.
AnthropicAdapter raises NotImplementedError for embed (no embedding API).
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class ModelAdapter(ABC):

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Single-turn text completion."""
        ...

    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        """Multi-turn chat completion.
        messages format: [{"role": "user"|"assistant"|"system", "content": str}]
        Returns the assistant reply as a plain string.
        """
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Produce a dense embedding vector for the given text."""
        ...