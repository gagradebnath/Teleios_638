"""
DocumentRetrievalTool — retrieve or index document blocks.
Dispatches on 'action':
  - "index"  → embed + store block in vector store and SQL
  - "fetch"  → retrieve blocks from SQL by doc_id / page

Permitted agents: document_agent, retrieval_agent, explanation_agent.
"""
from __future__ import annotations
from typing import Any

from tools.base_tool import BaseTool, ToolDefinition


class DocumentRetrievalTool(BaseTool):

    definition = ToolDefinition(
        name="document_retrieval",
        description="Retrieve raw or parsed document blocks by ID or page reference, or index new blocks",
        input_schema={
            "action":  "string: 'index' | 'fetch'",
            "doc_id":  "string",
            "page":    "integer | null",
            "text":    "string | null",
            "embedding": "array<float> | null",
            "title":   "string | null",
            "block_id": "string | null",
        },
        output_schema={
            "status": "string",
            "blocks": "array<DocumentBlock> | null",
        },
        permissions=["document_agent", "retrieval_agent", "explanation_agent"],
    )

    def __init__(self, vector_store, sql_store, ocr_service=None):
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
        embedding: list[float],
        block_id: str,
        **_,
    ) -> dict[str, Any]:
        try:
            # Store in vector index
            await self.vector_store.add(
                doc_id=doc_id,
                title=title,
                page=page,
                text=text,
                embedding=embedding,
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
            query  = "SELECT * FROM blocks WHERE doc_id = $1"
            params = [doc_id]
            if page is not None:
                query  += " AND page = $2"
                params.append(page)
            if block_type:
                idx     = len(params) + 1
                query  += f" AND block_type = ${idx}"
                params.append(block_type)
            rows = await self.sql_store.execute_query(query, params)
            return {"blocks": rows}
        except Exception as exc:
            return {"error": str(exc), "blocks": []}