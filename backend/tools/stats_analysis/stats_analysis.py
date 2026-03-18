"""
StatsAnalysisTool — topic frequency, recency scoring, and value normalization.
Used by qa_agent and prediction_agent to compute prediction score components.

Operations:
  frequency  — count topic occurrences across a list of question dicts
  recency    — exponential-decay score per year relative to today
  normalize  — min-max normalize a list of {id, value} dicts to [0, 1]
"""
from __future__ import annotations
import datetime
from typing import Any

from tools.base_tool import BaseTool, ToolDefinition


class StatsAnalysisTool(BaseTool):

    definition = ToolDefinition(
        name="stats_analysis",
        description="Compute topic frequency distributions, recency curves, and normalization",
        input_schema={
            "operation":   "string: 'frequency' | 'recency' | 'normalize'",
            "data":        "array",
            "decay_years": "integer | null",
        },
        output_schema={
            "result": "object",
        },
        permissions=["qa_agent", "prediction_agent"],
    )

    async def execute(
        self,
        operation: str,
        data: list,
        decay_years: int = 3,
        **_,
    ) -> dict[str, Any]:
        try:
            if operation == "frequency":
                return self._frequency(data)
            elif operation == "recency":
                return self._recency(data, decay_years)
            elif operation == "normalize":
                return self._normalize(data)
            else:
                return {"error": f"Unknown operation '{operation}'. Use: frequency, recency, normalize."}
        except Exception as exc:
            return {"error": str(exc)}

    # ── frequency ────────────────────────────────────────────────────────────

    def _frequency(self, data: list) -> dict:
        """
        Count how many times each topic appears.
        data: list of dicts with a "topic" key.
        Returns: {"frequency": {"calculus": 5, "algebra": 3, ...}}
        """
        counts: dict[str, int] = {}
        for item in data:
            topic = item.get("topic") or "unknown"
            counts[topic] = counts.get(topic, 0) + 1
        return {"frequency": counts}

    # ── recency ───────────────────────────────────────────────────────────────

    def _recency(self, data: list, decay_years: int) -> dict:
        """
        Score each year with exponential linear decay.
        score = max(0.0, 1.0 - (current_year - year) / decay_years)
        data: list of dicts with a "year" key (int).
        Returns: {"recency": {2024: 1.0, 2022: 0.33, ...}}
        """
        current_year = datetime.date.today().year
        scores: dict[int, float] = {}
        for item in data:
            year = item.get("year")
            if year is None:
                continue
            score = max(0.0, 1.0 - (current_year - int(year)) / decay_years)
            scores[int(year)] = round(score, 4)
        return {"recency": scores}

    # ── normalize ─────────────────────────────────────────────────────────────

    def _normalize(self, data: list) -> dict:
        """
        Min-max normalize a list of {id, value} dicts to [0, 1].
        Returns: {"normalized": [{"id": ..., "value": 0.75}, ...]}
        """
        if not data:
            return {"normalized": []}

        values = [float(item["value"]) for item in data]
        min_v  = min(values)
        max_v  = max(values)
        spread = max_v - min_v or 1.0   # avoid division by zero

        normalized = [
            {"id": item["id"], "value": round((float(item["value"]) - min_v) / spread, 4)}
            for item in data
        ]
        return {"normalized": normalized}