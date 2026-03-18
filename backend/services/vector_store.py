"""
VectorStoreService — ChromaDB vector index abstraction.
Handles add, search, and delete operations for document embeddings.

Host resolution order (first wins):
  1. CHROMA_HOST / CHROMA_PORT environment variables  (set by docker-compose)
  2. storage_config["chroma_host"] / ["chroma_port"]  (from config/app.json)
  3. Fallback: localhost:8001                          (pure local dev)
"""
from __future__ import annotations

import os
import structlog

logger = structlog.get_logger()


class VectorStoreService:

    def __init__(self, storage_config: dict):
        self.collection_name = storage_config.get("vector_collection", "teleios_docs")

        # Env vars take priority so docker-compose can override without touching config
        self._host = os.environ.get(
            "CHROMA_HOST",
            storage_config.get("chroma_host", "localhost"),
        )
        self._port = int(os.environ.get(
            "CHROMA_PORT",
            storage_config.get("chroma_port", 8001),
        ))

        self._collection = None   # lazy-initialised on first use

    async def _get_collection(self):
        """Lazy-init the ChromaDB collection (cosine distance)."""
        if self._collection is not None:
            return self._collection

        import chromadb
        client = await chromadb.AsyncHttpClient(host=self._host, port=self._port)
        self._collection = await client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("vector_store.ready",
                    collection=self.collection_name,
                    host=self._host,
                    port=self._port)
        return self._collection

    # ── Write ─────────────────────────────────────────────────────────────────

    async def add(
        self,
        doc_id: str,
        title: str,
        page: int,
        text: str,
        embedding: list[float],
        block_id: str,
    ) -> None:
        col = await self._get_collection()
        await col.upsert(
            ids=[block_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"doc_id": doc_id, "title": title, "page": page}],
        )

    async def delete_by_doc(self, doc_id: str) -> None:
        col = await self._get_collection()
        await col.delete(where={"doc_id": doc_id})
        logger.info("vector_store.deleted", doc_id=doc_id)

    # ── Search ────────────────────────────────────────────────────────────────

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 6,
        doc_id: str | None = None,
    ) -> list[dict]:
        col    = await self._get_collection()
        kwargs: dict = dict(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        if doc_id:
            kwargs["where"] = {"doc_id": doc_id}

        try:
            result = await col.query(**kwargs)
        except Exception as exc:
            logger.warning("vector_store.search_error", error=str(exc))
            return []

        ids       = result.get("ids",       [[]])[0]
        docs      = result.get("documents", [[]])[0]
        metas     = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        hits = []
        for i, block_id in enumerate(ids):
            meta     = metas[i] if i < len(metas) else {}
            distance = distances[i] if i < len(distances) else 1.0
            hits.append({
                "id":     block_id,
                "text":   docs[i] if i < len(docs) else "",
                "score":  round(1.0 - float(distance), 4),
                "doc_id": meta.get("doc_id", ""),
                "title":  meta.get("title",  ""),
                "page":   meta.get("page",   0),
            })

        return hits