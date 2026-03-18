"""
RetrievalAgent — Semantic search against vector store and SQL.
Retrieves relevant document blocks and context for QA/explanation.
"""
from __future__ import annotations
from typing import Any

import structlog
from agents.base_agent import BaseAgent

logger = structlog.get_logger()


class RetrievalAgent(BaseAgent):
    """Retrieves context from vector store and SQL."""

    def __init__(self, tools_registry: dict[str, Any] | None = None):
        super().__init__("retrieval_agent", tools_registry)

    async def run(
        self,
        query: str,
        top_k: int = 6,
        doc_id: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Retrieve context for a query.

        Args:
            query — search query
            top_k — number of results to return
            doc_id — optional doc filter

        Returns:
            {"status": "ok", "results": [...]} or {"status": "error", ...}
        """
        try:
            vector_search_tool = await self.get_tool("vector_search")
            results = await vector_search_tool.execute(
                query=query,
                top_k=top_k,
                doc_id=doc_id,
            )
            logger.info("retrieval_agent.search", query_len=len(query), results=len(results.get("results", [])))
            return {"status": "ok", **results}

        except Exception as exc:
            logger.error("retrieval_agent.error", error=str(exc))
            return {"status": "error", "error": str(exc), "results": []}
