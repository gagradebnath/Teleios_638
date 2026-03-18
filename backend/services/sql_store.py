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


def _to_sqlite(query: str, params: list) -> tuple[str, list]:
    """Replace $1, $2, ... positional markers with SQLite's ? placeholder."""
    q = re.sub(r"\$\d+", "?", query)
    return q, params


class SQLStoreService:

    # ── Generic query ─────────────────────────────────────────────────────────

    async def execute_query(self, query: str, params: list | None = None) -> list[dict]:
        """
        Run any parameterized SELECT and return rows as list of dicts.
        Supports both $1 (PostgreSQL-style) and ? (SQLite-style) placeholders.
        """
        q, p = _to_sqlite(query, params or [])
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
                    "VALUES (?, ?, ?, ?, ?, ?)"
                ),
                [
                    doc_id,
                    doc.get("title", "Untitled"),
                    doc.get("doc_type", "unknown"),
                    doc.get("year"),
                    doc.get("subject"),
                    doc.get("filename", ""),
                ],
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
                    "VALUES (?, ?, ?, ?, ?, ?)"
                ),
                [
                    block_id,
                    block["doc_id"],
                    block.get("block_type", "text"),
                    block.get("page", 0),
                    content,
                    block.get("embedding_id"),
                ],
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
                    "VALUES (?, ?, ?, ?, ?)"
                ),
                [
                    q_id,
                    question["doc_id"],
                    question["text"],
                    question.get("topic"),
                    question.get("year"),
                ],
            )
            await session.commit()
        return q_id

    async def get_questions_by_docs(self, doc_ids: list[str]) -> list[dict]:
        """Fetch all questions belonging to the given document IDs."""
        if not doc_ids:
            return []
        placeholders = ", ".join("?" * len(doc_ids))
        async with get_async_session() as session:
            result = await session.execute(
                text(
                    f"SELECT id, doc_id, text, topic, year, prediction_score "
                    f"FROM questions WHERE doc_id IN ({placeholders})"
                ),
                doc_ids,
            )
            keys = list(result.keys())
            return [dict(zip(keys, row)) for row in result.fetchall()]

    async def update_prediction_score(self, question_id: str, score: float) -> None:
        """Persist a freshly computed prediction score back to the DB."""
        async with get_async_session() as session:
            await session.execute(
                text(
                    "UPDATE questions SET prediction_score = ?, "
                    "last_scored_at = datetime('now') WHERE id = ?"
                ),
                [round(score, 6), question_id],
            )
            await session.commit()