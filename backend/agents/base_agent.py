"""
BaseAgent — Abstract base class for all agents.
Provides shared infrastructure: tool access, logging, adapter injection.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

import structlog
logger = structlog.get_logger()


class BaseAgent(ABC):
    """Abstract base agent. All agents inherit from this."""

    def __init__(self, agent_name: str, tools_registry: dict[str, Any] | None = None):
        """
        Args:
            agent_name — identifier for logging and permission checks
            tools_registry — dict of {tool_name: ToolInstance}
        """
        self.agent_name = agent_name
        self.tools_registry = tools_registry or {}
        self.adapter = None  # Injected by orchestrator

    def set_adapter(self, adapter) -> None:
        """Inject the ModelAdapter (called by orchestrator during setup)."""
        self.adapter = adapter

    def set_tools(self, tools_registry: dict[str, Any]) -> None:
        """Update or replace the tools registry."""
        self.tools_registry = tools_registry

    async def get_tool(self, tool_name: str):
        """Safely fetch a tool, check permissions, log access."""
        if tool_name not in self.tools_registry:
            logger.warning("tool.not_found", agent=self.agent_name, tool=tool_name)
            raise ValueError(f"Tool '{tool_name}' not found in registry")
        logger.debug("tool.access", agent=self.agent_name, tool=tool_name)
        return self.tools_registry[tool_name]

    @abstractmethod
    async def run(self, **kwargs) -> dict[str, Any]:
        """
        Execute the agent.
        Must be implemented by subclasses.
        Returns a structured result dict with at minimum {"status": "ok" | "error"}.
        """
        pass
