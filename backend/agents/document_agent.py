"""
DocumentAgent — Ingest PDFs, extract blocks (text/figure/equation/table), and index.
Dispatches: ingest_pdf action via tool.
"""
from __future__ import annotations
from typing import Any

import structlog
from agents.base_agent import BaseAgent

logger = structlog.get_logger()


class DocumentAgent(BaseAgent):
    """Ingests documents, extracts blocks, stores in DB and vector index."""

    def __init__(self, tools_registry: dict[str, Any] | None = None):
        super().__init__("document_agent", tools_registry)

    async def run(
        self,
        action: str,
        doc_id: str | None = None,
        title: str | None = None,
        doc_type: str = "unknown",
        blocks: list[dict] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Run document ingestion.

        Args:
            action — 'index' | 'fetch'
            doc_id — document ID (auto-generated if None)
            title — document title
            doc_type — 'textbook' | 'exam'
            blocks — list of {block_type, page, content, embedding?}

        Returns:
            {"status": "ok", "doc_id": ..., "blocks_indexed": N, ...}
            or {"status": "error", "error": ...}
        """
        try:
            if action == "index":
                return await self._index(
                    doc_id=doc_id,
                    title=title,
                    doc_type=doc_type,
                    blocks=blocks or [],
                    **kwargs,
                )
            elif action == "fetch":
                return await self._fetch(doc_id=doc_id, **kwargs)
            else:
                return {"status": "error", "error": f"Unknown action '{action}'"}

        except Exception as exc:
            logger.error("document_agent.error", error=str(exc))
            return {"status": "error", "error": str(exc)}

    async def _index(
        self,
        doc_id: str | None,
        title: str | None,
        doc_type: str,
        blocks: list[dict],
        course_id: str | None = None,
        file_system_node_id: str | None = None,
        file_path: str | None = None,
        file_size_bytes: int = 0,
        total_pages: int = 0,
        **_,
    ) -> dict[str, Any]:
        """Index a document and its blocks with enhanced metadata."""
        doc_retrieval_tool = await self.get_tool("document_retrieval")

        # Insert document with additional metadata
        doc_id_result = await doc_retrieval_tool.execute(
            action="index",
            doc_id=doc_id,
            title=title or "Untitled",
            page=0,
            text="",
            block_id="",
            course_id=course_id,
            file_system_node_id=file_system_node_id,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            total_pages=total_pages,
        )

        if "error" in doc_id_result:
            return {"status": "error", "error": doc_id_result["error"]}

        # Index blocks
        indexed_count = 0
        for i, block in enumerate(blocks):
            block_result = await doc_retrieval_tool.execute(
                action="index",
                doc_id=doc_id or doc_id_result.get("block_id", ""),
                title=title or "Untitled",
                page=block.get("page", 0),
                text=block.get("content", ""),
                embedding=block.get("embedding"),
                block_id=block.get("id", f"block-{i}"),
            )
            if "error" not in block_result:
                indexed_count += 1

        logger.info("document_agent.indexed", count=indexed_count, course_id=course_id)
        final_doc_id = doc_id or doc_id_result.get("block_id", f"doc-{doc_id_result.get('id', 'unknown')}")
        return {
            "status": "ok",
            "doc_id": final_doc_id,
            "title": title or "Untitled",
            "blocks_indexed": indexed_count,
        }

    async def _fetch(self, doc_id: str, **_) -> dict[str, Any]:
        """Fetch document blocks by doc_id."""
        doc_retrieval_tool = await self.get_tool("document_retrieval")
        result = await doc_retrieval_tool.execute(action="fetch", doc_id=doc_id)
        return {"status": "ok", **result}
