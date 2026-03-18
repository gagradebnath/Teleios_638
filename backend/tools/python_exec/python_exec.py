"""
PythonExecTool — sandboxed Python execution via SandboxService.
Only permitted for execution_agent. All code runs inside RestrictedPython.
"""
from __future__ import annotations
from typing import Any

from tools.base_tool import BaseTool


class PythonExecTool(BaseTool):

    def __init__(self, sandbox):
        super().__init__("python_exec")
        self.sandbox = sandbox

    async def execute(self, code: str, timeout_seconds: int = 10) -> dict[str, Any]:
        try:
            result = self.sandbox.execute(code, timeout_seconds)
            return result
        except Exception as exc:
            return {"stdout": "", "figures": [], "error": str(exc)}