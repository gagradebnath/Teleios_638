"""
SQLStoreService — async SQLite wrapper via SQLAlchemy.
Note: SQLite uses ? placeholders, not $1. This service normalises both.
"""
from __future__ import annotations
import json
import re
import uuid

from sqlalchemy import text
from db.session import get_async_session


def _to_sqlite_params(query: str, params: list):
    """Replace $1, $2, ... with ? for SQLite."""
    q = re.sub(r"\$\d+", "?", query)
    return q, params


class SQLStoreService:

    async def execute_query(self, query: str, params: list = None) -> list[dict]:
        q, p = _to_sqlite_params(query, params or [])
        async with get_async_session() as session:
            result = await session.execute(text(q), p)
            rows = result.fetchall()
            keys = result.keys()
            return [dict(zip(keys, row)) for row in rows]

    async def insert_document(self, doc: dict) -> str:
        doc.setdefault("id", str(uuid.uuid4()))
        async with get_async_session() as session:
            await session.execute(
                text("INSERT INTO documents (id, title, doc_type, year, subject, filename) "
                     "VALUES (?, ?, ?, ?, ?, ?)"),
                [doc["id"], doc["title"], doc.get("doc_type","unknown"),
                 doc.get("year"), doc.get("subject"), doc["filename"]]
            )
            await session.commit()
        return doc["id"]

    async def insert_block(self, block: dict) -> str:
        block.setdefault("id", str(uuid.uuid4()))
        content = block["content"] if isinstance(block["content"], str) else json.dumps(block["content"])
        async with get_async_session() as session:
            await session.execute(
                text("INSERT INTO blocks (id, doc_id, block_type, page, content, embedding_id) "
                     "VALUES (?, ?, ?, ?, ?, ?)"),
                [block["id"], block["doc_id"], block["block_type"],
                 block.get("page", 0), content, block.get("embedding_id")]
            )
            await session.commit()
        return block["id"]

    async def insert_question(self, question: dict) -> str:
        question.setdefault("id", str(uuid.uuid4()))
        async with get_async_session() as session:
            await session.execute(
                text("INSERT INTO questions (id, doc_id, text, topic, year) VALUES (?, ?, ?, ?, ?)"),
                [question["id"], question["doc_id"], question["text"],
                 question.get("topic"), question.get("year")]
            )
            await session.commit()
        return question["id"]

    async def get_questions_by_docs(self, doc_ids: list[str]) -> list[dict]:
        if not doc_ids:
            return []
        placeholders = ", ".join("?" * len(doc_ids))
        async with get_async_session() as session:
            result = await session.execute(
                text(f"SELECT id, doc_id, text, topic, year, prediction_score FROM questions WHERE doc_id IN ({placeholders})"),
                doc_ids
            )
            rows = result.fetchall()
            keys = result.keys()
            return [dict(zip(keys, row)) for row in rows]