# this is the base class for document retrieval, python execution, 
# registry, sql_query, stat_analysis, vector_search, web_search


# BaseTool — abstract base for all MCP tools.
# Every tool must define a ToolDefinition and implement execute().
# The Orchestrator enforces permissions before any agent can invoke a tool.

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict
    output_schema: dict
    permissions: list[str]

    def __int__(self,):
        



class BaseTool(ABC):
    definition: ToolDefinition

    @abstractmethod
    async def execute(self, **kwargs) -> dict[str, Any]:
        """
        Execute the tool with the given keyword arguments.
        Must return a plain dict matching the tool's output_schema.
        Never raises — errors are returned as {"error": str}.
        """
        ...


