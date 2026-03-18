"""
PythonExecTool — sandboxed Python execution via SandboxService.
Only permitted for execution_agent. All code runs inside RestrictedPython.
"""
from __future__ import annotations
from typing import Any

from tools.base_tool import BaseTool, ToolDefinition


class PythonExecTool(BaseTool):

    definition = ToolDefinition(
        name="python_exec",
        description="Sandboxed Python execution with math/science libraries (sympy, numpy, scipy, matplotlib)",
        input_schema={
            "code":            "string",
            "timeout_seconds": "integer",
        },
        output_schema={
            "stdout":  "string",
            "figures": "array<base64_png_string>",
            "error":   "string | null",
        },
        permissions=["execution_agent"],
    )

    def __init__(self, sandbox):
        self.sandbox = sandbox

    async def execute(self, code: str, timeout_seconds: int = 10) -> dict[str, Any]:
        try:
            result = self.sandbox.execute(code, timeout_seconds)
            return result
        except Exception as exc:
            return {"stdout": "", "figures": [], "error": str(exc)}