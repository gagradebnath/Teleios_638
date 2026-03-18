"""services/sql_store.py — Thin async wrapper around the SQLite DB."""
from __future__ import annotations
import json
import uuid
from datetime import datetime, UTC
from typing import Any

from sqlalchemy import text
from db.session import get_async_session


class SQLStoreService:

    async def insert_document(self, data: dict) -> str:
        doc_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO documents (id, title, doc_type, year, subject, filename, uploaded_at)
                VALUES (:id, :title, :doc_type, :year, :subject, :filename, :uploaded_at)
            """), {
                "id": doc_id,
                "title": data["title"],
                "doc_type": data.get("doc_type", "unknown"),
                "year": data.get("year"),
                "subject": data.get("subject"),
                "filename": data["filename"],
                "uploaded_at": datetime.now(UTC).isoformat(),
            })
            await s.commit()
        return doc_id

    async def insert_block(self, data: dict) -> str:
        block_id = str(uuid.uuid4())
        content = data["content"]
        if not isinstance(content, str):
            content = json.dumps(content)
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO blocks (id, doc_id, block_type, page, content, created_at)
                VALUES (:id, :doc_id, :block_type, :page, :content, :created_at)
            """), {
                "id": block_id,
                "doc_id": data["doc_id"],
                "block_type": data.get("block_type", "text"),
                "page": data.get("page", 0),
                "content": content,
                "created_at": datetime.now(UTC).isoformat(),
            })
            await s.commit()
        return block_id

    async def insert_question(self, data: dict) -> str:
        q_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO questions (id, doc_id, text, topic, year, prediction_score)
                VALUES (:id, :doc_id, :text, :topic, :year, :prediction_score)
            """), {
                "id": q_id,
                "doc_id": data["doc_id"],
                "text": data["text"],
                "topic": data.get("topic"),
                "year": data.get("year"),
                "prediction_score": data.get("prediction_score", 0.0),
            })
            await s.commit()
        return q_id

    async def update_prediction_score(self, question_id: str, score: float) -> None:
        async with get_async_session() as s:
            await s.execute(text("""
                UPDATE questions
                SET prediction_score = :score, last_scored_at = :ts
                WHERE id = :id
            """), {"score": score, "ts": datetime.now(UTC).isoformat(), "id": question_id})
            await s.commit()

    async def execute_query(self, sql: str, params: list = None) -> list[dict[str, Any]]:
        """Run a raw SELECT and return rows as dicts. Uses positional ? placeholders."""
        named_sql = sql
        named_params: dict = {}
        if params:
            for i, val in enumerate(params):
                key = f"p{i}"
                named_sql = named_sql.replace("?", f":{key}", 1)
                named_params[key] = val
        async with get_async_session() as s:
            result = await s.execute(text(named_sql), named_params)
            cols = list(result.keys())
            return [dict(zip(cols, row)) for row in result.fetchall()]