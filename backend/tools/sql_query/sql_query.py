"""
SQLQueryTool — parameterized SQL queries against PostgreSQL.
Destructive statements (DROP, DELETE, TRUNCATE, ALTER) are blocked at this layer.
Permitted agents: qa_agent, prediction_agent, explanation_agent.
"""
from __future__ import annotations
import re
from typing import Any

from tools.base_tool import BaseTool, ToolDefinition

_BLOCKED = re.compile(r"\b(DROP|DELETE|TRUNCATE|ALTER)\b", re.IGNORECASE)


class SQLQueryTool(BaseTool):

    definition = ToolDefinition(
        name="sql_query",
        description="Parameterized SQL query against PostgreSQL",
        input_schema={
            "query":  "string",
            "params": "array",
        },
        output_schema={
            "rows":  "array",
            "count": "integer",
        },
        permissions=["qa_agent", "prediction_agent", "explanation_agent"],
    )

    def __init__(self, sql_store):
        self.sql_store = sql_store

    async def execute(self, query: str, params: list | None = None) -> dict[str, Any]:
        # Guard: block destructive statements
        if _BLOCKED.search(query):
            return {"error": "Destructive queries are not permitted.", "rows": [], "count": 0}

        try:
            rows = await self.sql_store.execute_query(query, params or [])
            return {"rows": rows, "count": len(rows)}
        except Exception as exc:
            return {"error": str(exc), "rows": [], "count": 0}