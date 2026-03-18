"""BaseTool and ToolDefinition utilities.

This module centralizes loading tool metadata from config/tools.json so that
child tool classes do not hard-code definitions. Each tool passes its name to
BaseTool.__init__, which loads the matching entry and populates self.definition.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, List

from pydantic import BaseModel


_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "tools.json"


def _permissions_to_list(raw: Any) -> List[str]:
    """Normalize permissions field from config into a list of agent names."""
    if isinstance(raw, dict):
        return [name for name, allowed in raw.items() if allowed]
    if isinstance(raw, Iterable) and not isinstance(raw, (str, bytes)):
        return list(raw)
    return []


@lru_cache(maxsize=1)
def _load_tools_config(config_path: Path = _CONFIG_PATH) -> list[dict[str, Any]]:
    if not config_path.exists():
        raise FileNotFoundError(f"tools config not found at {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("tools", [])


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict
    output_schema: dict
    permissions: list[str]

    @classmethod
    def from_config(cls, tool_name: str, config_path: Path | None = None) -> "ToolDefinition":
        path = Path(config_path) if config_path else _CONFIG_PATH
        for tool in _load_tools_config(path):
            if tool.get("name") == tool_name:
                return cls(
                    name=tool.get("name", tool_name),
                    description=tool.get("description", ""),
                    input_schema=tool.get("input_schema", {}),
                    output_schema=tool.get("output_schema", {}),
                    permissions=_permissions_to_list(tool.get("permissions", [])),
                )
        raise ValueError(f"Tool '{tool_name}' not found in {path}")


class BaseTool(ABC):
    definition: ToolDefinition

    def __init__(self, tool_name: str, config_path: str | Path | None = None) -> None:
        """Load tool definition from config and attach to the instance."""
        self.definition = ToolDefinition.from_config(tool_name, config_path)

    @abstractmethod
    async def execute(self, **kwargs) -> dict[str, Any]:
        """Execute the tool with the given keyword arguments."""
        ...


