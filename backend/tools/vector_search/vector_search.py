"""
VectorSearchTool — semantic similarity search against the indexed document collection.
Embeds the query via the ModelAdapter, then queries ChromaDB.
Permitted agents: retrieval_agent, explanation_agent, qa_agent.
"""
from __future__ import annotations
from typing import Any

from tools.base_tool import BaseTool


class VectorSearchTool(BaseTool):

    def __init__(self, adapter, vector_store):
        """
        adapter      — ModelAdapter instance (may be None at registry build time;
                       call set_adapter() before first use)
        vector_store — VectorStoreService instance
        """
        super().__init__("vector_search")
        self.adapter      = adapter
        self.vector_store = vector_store

    def set_adapter(self, adapter) -> None:
        """Inject the adapter after construction (called by main.py lifespan)."""
        self.adapter = adapter

    async def execute(self, query: str, top_k: int = 6, doc_id: str | None = None) -> dict[str, Any]:
        if self.adapter is None:
            return {"error": "VectorSearchTool: adapter not set. Call set_adapter() first."}
        try:
            embedding = await self.adapter.embed(query)
            results   = await self.vector_store.search(embedding, top_k=top_k, doc_id=doc_id)
            return {"results": results}
        except Exception as exc:
            return {"error": str(exc), "results": []}