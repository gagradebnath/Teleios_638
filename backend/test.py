"""Database smoke tests for SQLite wiring and SQLStoreService (sync-friendly)."""
from __future__ import annotations
import asyncio
from pathlib import Path

import pytest
from sqlalchemy import text

from db.session import init_db, get_async_session, close_db
from services.sql_store import SQLStoreService


def _run(coro):
	"""Helper to run async coroutines inside sync tests."""
	return asyncio.run(coro)


@pytest.fixture(scope="module")
def test_db(tmp_path_factory):
	"""Initialise a throwaway SQLite DB for this test module."""
	db_file = Path(tmp_path_factory.mktemp("data")) / "test.db"
	_run(init_db(f"sqlite+aiosqlite:///{db_file}"))
	yield
	_run(close_db())


def test_tables_exist(test_db):
	async def check():
		async with get_async_session() as session:
			result = await session.execute(
				text(
					"SELECT name FROM sqlite_master WHERE type='table' AND name IN ('documents','blocks','questions')"
				)
			)
			names = {row[0] for row in result.fetchall()}
			assert {"documents", "blocks", "questions"}.issubset(names)

	_run(check())


def test_insert_document_and_fetch(test_db):
	async def check():
		store = SQLStoreService()
		doc_id = await store.insert_document({
			"title": "Sample Doc",
			"doc_type": "unknown",  # ✅ valid: 'textbook' | 'past_paper' | 'unknown'
			"year": 2024,
			"subject": "math",
			"filename": "sample.pdf",
		})

		rows = await store.execute_query(
			"SELECT id, title, subject FROM documents WHERE id = ?",
			[doc_id],
		)
		assert len(rows) == 1
		assert rows[0]["title"] == "Sample Doc"
		assert rows[0]["subject"] == "math"

	_run(check())


def test_block_and_question_roundtrip(test_db):
	async def check():
		store = SQLStoreService()
		# ✅ fixed: "exam" is not a valid doc_type, use "past_paper"
		doc_id = await store.insert_document({"title": "Doc", "doc_type": "past_paper", "filename": "doc.pdf"})

		block_id = await store.insert_block({
			"doc_id": doc_id,
			"block_type": "text",
			"page": 1,
			"content": {"text": "Hello world"},
		})
		question_id = await store.insert_question({
			"doc_id": doc_id,
			"text": "What is 2+2?",
			"topic": "math",
			"year": 2023,
		})
		await store.update_prediction_score(question_id, 0.85)

		block_rows = await store.execute_query(
			"SELECT id, doc_id, block_type, page FROM blocks WHERE id = ?",
			[block_id],
		)
		q_rows = await store.execute_query(
			"SELECT id, prediction_score FROM questions WHERE id = ?",
			[question_id],
		)

		assert block_rows and block_rows[0]["doc_id"] == doc_id
		assert q_rows and abs(q_rows[0]["prediction_score"] - 0.85) < 1e-6

	_run(check())


if __name__ == "__main__":
	pytest.main([__file__, "-v"])