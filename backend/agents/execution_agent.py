"""
ExecutionAgent — Run sandboxed Python code and return results.
Uses python_exec tool which validates and restricts execution.
"""
from __future__ import annotations
from typing import Any

import structlog
from agents.base_agent import BaseAgent

logger = structlog.get_logger()


class ExecutionAgent(BaseAgent):
    """Executes sandboxed Python code."""

    def __init__(self, tools_registry: dict[str, Any] | None = None):
        super().__init__("execution_agent", tools_registry)

    async def run(
        self,
        code: str,
        timeout: int = 30,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Execute Python code in sandbox.

        Args:
            code — Python source code to run
            timeout — execution timeout in seconds

        Returns:
            {"status": "ok", "output": "...", "errors": []}
            or {"status": "error", ...}
        """
        try:
            python_exec_tool = await self.get_tool("python_exec")
            result = await python_exec_tool.execute(code=code, timeout=timeout)

            logger.info("execution_agent.executed", code_len=len(code), timeout=timeout)
            return {"status": "ok", **result}

        except Exception as exc:
            logger.error("execution_agent.error", error=str(exc))
            return {"status": "error", "error": str(exc), "output": "", "errors": [str(exc)]}
