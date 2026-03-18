"""
VectorStoreService — ChromaDB vector index abstraction.
Handles add, search, and delete operations for document embeddings.
All text blocks from ingested PDFs are stored here for semantic retrieval.
"""
from __future__ import annotations
import structlog

logger = structlog.get_logger()


class VectorStoreService:

    def __init__(self, storage_config: dict):
        """
        storage_config keys used:
          vector_collection — name of the ChromaDB collection
          vector_backend    — must be "chroma" (future: "faiss")
        ChromaDB is expected at http://chroma:8001 (docker service name).
        """
        self.collection_name = storage_config.get("vector_collection", "teleios_docs")
        self._collection = None   # lazy-initialised on first use

    async def _get_collection(self):
        """Lazy-init the ChromaDB collection (cosine distance)."""
        if self._collection is not None:
            return self._collection

        import chromadb
        client = await chromadb.AsyncHttpClient(host="chroma", port=8001)
        self._collection = await client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("vector_store.ready", collection=self.collection_name)
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
        """
        Upsert a single text block into the collection.
        block_id is the unique ChromaDB document id.
        Metadata allows filtering by doc_id at search time.
        """
        col = await self._get_collection()
        await col.upsert(
            ids=[block_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "doc_id": doc_id,
                "title":  title,
                "page":   page,
            }],
        )

    async def delete_by_doc(self, doc_id: str) -> None:
        """Remove all vectors associated with a document."""
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
        """
        Semantic search. Optionally filter by doc_id.
        Returns list of:
          {id, text, score, doc_id, title, page}
        Score is cosine similarity (0–1, higher = more similar).
        """
        col    = await self._get_collection()
        kwargs = dict(
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

        hits = []
        ids       = result.get("ids",       [[]])[0]
        docs      = result.get("documents", [[]])[0]
        metas     = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        for i, block_id in enumerate(ids):
            meta = metas[i] if i < len(metas) else {}
            # ChromaDB cosine distance → similarity: score = 1 - distance
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