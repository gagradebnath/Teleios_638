"""
SQLStoreService — async SQLite wrapper via SQLAlchemy + aiosqlite.
All queries use ? placeholders (SQLite style).
$1, $2 ... placeholders from agent code are auto-converted.
"""
from __future__ import annotations
import json
import re
import uuid

from sqlalchemy import text
from db.session import get_async_session

import structlog
logger = structlog.get_logger()


def _normalize_params(query: str, params: list | tuple) -> tuple[str, dict]:
    """Support $n or ? placeholders by converting to named binds for SQLAlchemy."""
    if params is None:
        params = []
    params = list(params)

    # Handle PostgreSQL-style $1, $2
    if "$" in query:
        def repl(match):
            idx = int(match.group()[1:]) - 1
            return f":p{idx}"
        query = re.sub(r"\$\d+", repl, query)
        bind_params = {f"p{i}": val for i, val in enumerate(params)}
        return query, bind_params

    # Handle ? placeholders
    if "?" in query:
        parts = query.split("?")
        rebuilt = []
        bind_params = {}
        for i, part in enumerate(parts[:-1]):
            rebuilt.append(part)
            rebuilt.append(f":p{i}")
            bind_params[f"p{i}"] = params[i] if i < len(params) else None
        rebuilt.append(parts[-1])
        return "".join(rebuilt), bind_params

    # No placeholders
    return query, {}


class SQLStoreService:

    # ── Generic query ─────────────────────────────────────────────────────────

    async def execute_query(self, query: str, params: list | None = None) -> list[dict]:
        """
        Run any parameterized SELECT and return rows as list of dicts.
        Supports both $1 (PostgreSQL-style) and ? (SQLite-style) placeholders.
        """
        q, p = _normalize_params(query, params or [])
        async with get_async_session() as session:
            result = await session.execute(text(q), p)
            keys   = list(result.keys())
            rows   = result.fetchall()
            return [dict(zip(keys, row)) for row in rows]

    # ── Documents ─────────────────────────────────────────────────────────────

    async def insert_document(self, doc: dict) -> str:
        """Insert a document record. Returns the id."""
        doc_id = doc.get("id") or str(uuid.uuid4())
        async with get_async_session() as session:
            await session.execute(
                text(
                    "INSERT INTO documents (id, title, doc_type, year, subject, filename) "
                    "VALUES (:id, :title, :doc_type, :year, :subject, :filename)"
                ),
                {
                    "id": doc_id,
                    "title": doc.get("title", "Untitled"),
                    "doc_type": doc.get("doc_type", "unknown"),
                    "year": doc.get("year"),
                    "subject": doc.get("subject"),
                    "filename": doc.get("filename", ""),
                },
            )
            await session.commit()
        logger.debug("sql_store.insert_document", doc_id=doc_id)
        return doc_id

    # ── Blocks ────────────────────────────────────────────────────────────────

    async def insert_block(self, block: dict) -> str:
        """Insert a document block. Content dict is JSON-serialized."""
        block_id = block.get("id") or str(uuid.uuid4())
        content  = block["content"]
        if not isinstance(content, str):
            content = json.dumps(content)

        async with get_async_session() as session:
            await session.execute(
                text(
                    "INSERT INTO blocks (id, doc_id, block_type, page, content, embedding_id) "
                    "VALUES (:id, :doc_id, :block_type, :page, :content, :embedding_id)"
                ),
                {
                    "id": block_id,
                    "doc_id": block["doc_id"],
                    "block_type": block.get("block_type", "text"),
                    "page": block.get("page", 0),
                    "content": content,
                    "embedding_id": block.get("embedding_id"),
                },
            )
            await session.commit()
        return block_id

    # ── Questions ─────────────────────────────────────────────────────────────

    async def insert_question(self, question: dict) -> str:
        """Insert an extracted exam question."""
        q_id = question.get("id") or str(uuid.uuid4())
        async with get_async_session() as session:
            await session.execute(
                text(
                    "INSERT INTO questions (id, doc_id, text, topic, year) "
                    "VALUES (:id, :doc_id, :text, :topic, :year)"
                ),
                {
                    "id": q_id,
                    "doc_id": question["doc_id"],
                    "text": question["text"],
                    "topic": question.get("topic"),
                    "year": question.get("year"),
                },
            )
            await session.commit()
        return q_id

    async def get_questions_by_docs(self, doc_ids: list[str]) -> list[dict]:
        """Fetch all questions belonging to the given document IDs."""
        if not doc_ids:
            return []
        placeholders = ", ".join(f":p{i}" for i in range(len(doc_ids)))
        async with get_async_session() as session:
            result = await session.execute(
                text(
                    f"SELECT id, doc_id, text, topic, year, prediction_score "
                    f"FROM questions WHERE doc_id IN ({placeholders})"
                ),
                {f"p{i}": doc_ids[i] for i in range(len(doc_ids))},
            )
            keys = list(result.keys())
            return [dict(zip(keys, row)) for row in result.fetchall()]

    async def update_prediction_score(self, question_id: str, score: float) -> None:
        """Persist a freshly computed prediction score back to the DB."""
        async with get_async_session() as session:
            await session.execute(
                text(
                    "UPDATE questions SET prediction_score = :score, "
                    "last_scored_at = datetime('now') WHERE id = :id"
                ),
                {"score": round(score, 6), "id": question_id},
            )
            await session.commit()