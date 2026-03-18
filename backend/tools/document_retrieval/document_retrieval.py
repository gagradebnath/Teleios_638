"""
DocumentRetrievalTool — retrieve or index document blocks.
Dispatches on 'action':
  - "index"  → embed + store block in vector store and SQL
  - "fetch"  → retrieve blocks from SQL by doc_id / page

Permitted agents: document_agent, retrieval_agent, explanation_agent.
"""
from __future__ import annotations
from typing import Any

from tools.base_tool import BaseTool


class DocumentRetrievalTool(BaseTool):

    def __init__(self, vector_store, sql_store, ocr_service=None):
        super().__init__("document_retrieval")
        self.vector_store = vector_store
        self.sql_store    = sql_store
        self.ocr_service  = ocr_service
        self.adapter      = None  # injected via set_adapter()

    def set_adapter(self, adapter) -> None:
        self.adapter = adapter

    async def execute(self, action: str, **kwargs) -> dict[str, Any]:
        if action == "index":
            return await self._index(**kwargs)
        elif action == "fetch":
            return await self._fetch(**kwargs)
        else:
            return {"error": f"Unknown action '{action}'. Use 'index' or 'fetch'."}

    async def _index(
        self,
        doc_id: str,
        title: str,
        page: int,
        text: str,
        embedding: list[float] | None,
        block_id: str,
        **_,
    ) -> dict[str, Any]:
        try:
            if embedding is None and self.adapter is not None:
                embedding = await self.adapter.embed(text)
            # Store in vector index
            await self.vector_store.add(
                doc_id=doc_id,
                title=title,
                page=page,
                text=text,
                embedding=embedding or [],
                block_id=block_id,
            )
            return {"status": "indexed", "block_id": block_id}
        except Exception as exc:
            return {"error": str(exc), "status": "failed"}

    async def _fetch(
        self,
        doc_id: str,
        page: int | None = None,
        block_type: str | None = None,
        **_,
    ) -> dict[str, Any]:
        try:
            query  = "SELECT * FROM blocks WHERE doc_id = :doc_id"
            params = {"doc_id": doc_id}
            if page is not None:
                query  += " AND page = :page"
                params["page"] = page
            if block_type:
                query  += " AND block_type = :block_type"
                params["block_type"] = block_type
            rows = await self.sql_store.execute_query(query, params)
            return {"blocks": rows}
        except Exception as exc:
            return {"error": str(exc), "blocks": []}