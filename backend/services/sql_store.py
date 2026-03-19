"""services/sql_store.py — Thin async wrapper around the SQLite DB.
Enhanced with support for courses, file system, knowledge base, and study tracking.
"""
from __future__ import annotations
import json
import uuid
from datetime import datetime, UTC
from typing import Any, Optional

from sqlalchemy import text
from db.session import get_async_session


class SQLStoreService:

    # ══════════════════════════════════════════════════════════════════════════
    # COURSES
    # ══════════════════════════════════════════════════════════════════════════

    async def insert_course(self, data: dict) -> str:
        """Create a new course."""
        course_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO courses (id, name, code, description, color, created_at, updated_at)
                VALUES (:id, :name, :code, :description, :color, :created_at, :updated_at)
            """), {
                "id": course_id,
                "name": data["name"],
                "code": data.get("code"),
                "description": data.get("description"),
                "color": data.get("color", "#3b82f6"),
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            })
            await s.commit()
        return course_id

    async def list_courses(self) -> list[dict[str, Any]]:
        """Get all courses."""
        return await self.execute_query("SELECT * FROM courses ORDER BY name")

    async def get_course(self, course_id: str) -> Optional[dict[str, Any]]:
        """Get a single course by ID."""
        results = await self.execute_query("SELECT * FROM courses WHERE id = ?", [course_id])
        return results[0] if results else None

    # ══════════════════════════════════════════════════════════════════════════
    # FILE SYSTEM
    # ══════════════════════════════════════════════════════════════════════════

    async def insert_file_system_node(self, data: dict) -> str:
        """Create a file or folder node."""
        node_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO file_system_nodes 
                (id, parent_id, course_id, name, node_type, path, size_bytes, mime_type, created_at, updated_at)
                VALUES (:id, :parent_id, :course_id, :name, :node_type, :path, :size_bytes, :mime_type, :created_at, :updated_at)
            """), {
                "id": node_id,
                "parent_id": data.get("parent_id"),
                "course_id": data.get("course_id"),
                "name": data["name"],
                "node_type": data.get("node_type", "file"),
                "path": data["path"],
                "size_bytes": data.get("size_bytes", 0),
                "mime_type": data.get("mime_type"),
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            })
            await s.commit()
        return node_id

    async def list_file_system_nodes(self, parent_id: Optional[str] = None, course_id: Optional[str] = None) -> list[dict[str, Any]]:
        """List files/folders in a directory or course."""
        if parent_id:
            return await self.execute_query(
                "SELECT * FROM file_system_nodes WHERE parent_id = ? ORDER BY node_type DESC, name",
                [parent_id]
            )
        elif course_id:
            return await self.execute_query(
                "SELECT * FROM file_system_nodes WHERE course_id = ? AND parent_id IS NULL ORDER BY node_type DESC, name",
                [course_id]
            )
        else:
            return await self.execute_query(
                "SELECT * FROM file_system_nodes WHERE parent_id IS NULL ORDER BY node_type DESC, name"
            )

    async def get_file_system_node(self, node_id: str) -> Optional[dict[str, Any]]:
        """Get a single file system node."""
        results = await self.execute_query("SELECT * FROM file_system_nodes WHERE id = ?", [node_id])
        return results[0] if results else None

    async def delete_file_system_node(self, node_id: str) -> None:
        """Delete a file/folder node (cascades to children)."""
        async with get_async_session() as s:
            await s.execute(text("DELETE FROM file_system_nodes WHERE id = :id"), {"id": node_id})
            await s.commit()

    # ══════════════════════════════════════════════════════════════════════════
    # DOCUMENTS (Enhanced)
    # ══════════════════════════════════════════════════════════════════════════

    async def insert_document(self, data: dict) -> str:
        """Create a document with enhanced fields."""
        doc_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO documents 
                (id, title, doc_type, year, subject, filename, uploaded_at,
                 course_id, file_system_node_id, processing_status, total_pages, 
                 file_size_bytes, file_path, doc_metadata)
                VALUES (:id, :title, :doc_type, :year, :subject, :filename, :uploaded_at,
                        :course_id, :file_system_node_id, :processing_status, :total_pages,
                        :file_size_bytes, :file_path, :doc_metadata)
            """), {
                "id": doc_id,
                "title": data["title"],
                "doc_type": data.get("doc_type", "unknown"),
                "year": data.get("year"),
                "subject": data.get("subject"),
                "filename": data["filename"],
                "uploaded_at": datetime.now(UTC).isoformat(),
                "course_id": data.get("course_id"),
                "file_system_node_id": data.get("file_system_node_id"),
                "processing_status": data.get("processing_status", "pending"),
                "total_pages": data.get("total_pages", 0),
                "file_size_bytes": data.get("file_size_bytes", 0),
                "file_path": data.get("file_path"),
                "doc_metadata": json.dumps(data.get("doc_metadata")) if data.get("doc_metadata") else None,
            })
            await s.commit()
        return doc_id

    async def update_document_status(self, doc_id: str, status: str) -> None:
        """Update document processing status."""
        async with get_async_session() as s:
            await s.execute(text("""
                UPDATE documents SET processing_status = :status WHERE id = :id
            """), {"status": status, "id": doc_id})
            await s.commit()

    async def get_document(self, doc_id: str) -> Optional[dict[str, Any]]:
        """Get a single document."""
        results = await self.execute_query("SELECT * FROM documents WHERE id = ?", [doc_id])
        return results[0] if results else None

    async def list_documents(self, course_id: Optional[str] = None) -> list[dict[str, Any]]:
        """List all documents, optionally filtered by course."""
        if course_id:
            return await self.execute_query(
                "SELECT * FROM documents WHERE course_id = ? ORDER BY uploaded_at DESC",
                [course_id]
            )
        return await self.execute_query("SELECT * FROM documents ORDER BY uploaded_at DESC")

    # ══════════════════════════════════════════════════════════════════════════
    # DOCUMENT PAGES
    # ══════════════════════════════════════════════════════════════════════════

    async def insert_document_page(self, data: dict) -> str:
        """Create document page metadata."""
        page_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO document_pages 
                (id, doc_id, page_number, width, height, has_text, has_images, has_math, thumbnail, processed, created_at)
                VALUES (:id, :doc_id, :page_number, :width, :height, :has_text, :has_images, :has_math, :thumbnail, :processed, :created_at)
            """), {
                "id": page_id,
                "doc_id": data["doc_id"],
                "page_number": data["page_number"],
                "width": data.get("width"),
                "height": data.get("height"),
                "has_text": data.get("has_text", True),
                "has_images": data.get("has_images", False),
                "has_math": data.get("has_math", False),
                "thumbnail": data.get("thumbnail"),
                "processed": data.get("processed", False),
                "created_at": datetime.now(UTC).isoformat(),
            })
            await s.commit()
        return page_id

    async def get_document_pages(self, doc_id: str) -> list[dict[str, Any]]:
        """Get all pages for a document."""
        return await self.execute_query(
            "SELECT * FROM document_pages WHERE doc_id = ? ORDER BY page_number",
            [doc_id]
        )

    # ══════════════════════════════════════════════════════════════════════════
    # RAW EXTRACTIONS
    # ══════════════════════════════════════════════════════════════════════════

    async def insert_raw_extraction(self, data: dict) -> str:
        """Store raw OCR output."""
        extraction_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO raw_extractions 
                (id, doc_id, page_number, raw_text, extraction_metadata, created_at, processed)
                VALUES (:id, :doc_id, :page_number, :raw_text, :extraction_metadata, :created_at, :processed)
            """), {
                "id": extraction_id,
                "doc_id": data["doc_id"],
                "page_number": data["page_number"],
                "raw_text": data["raw_text"],
                "extraction_metadata": json.dumps(data.get("extraction_metadata")) if data.get("extraction_metadata") else None,
                "created_at": datetime.now(UTC).isoformat(),
                "processed": data.get("processed", False),
            })
            await s.commit()
        return extraction_id

    async def get_unprocessed_raw_extractions(self, doc_id: str) -> list[dict[str, Any]]:
        """Get raw extractions that haven't been cleaned by LLM yet."""
        return await self.execute_query(
            "SELECT * FROM raw_extractions WHERE doc_id = ? AND processed = 0 ORDER BY page_number",
            [doc_id]
        )

    async def mark_raw_extraction_processed(self, extraction_id: str) -> None:
        """Mark a raw extraction as processed."""
        async with get_async_session() as s:
            await s.execute(text("""
                UPDATE raw_extractions SET processed = 1 WHERE id = :id
            """), {"id": extraction_id})
            await s.commit()

    # ══════════════════════════════════════════════════════════════════════════
    # BLOCKS (Enhanced)
    # ══════════════════════════════════════════════════════════════════════════

    async def insert_block(self, data: dict) -> str:
        """Create a block with enhanced fields."""
        block_id = str(uuid.uuid4())
        content = data["content"]
        if not isinstance(content, str):
            content = json.dumps(content)
        
        llm_cleaned = data.get("llm_cleaned_content")
        if llm_cleaned and not isinstance(llm_cleaned, str):
            llm_cleaned = json.dumps(llm_cleaned)
        
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO blocks 
                (id, doc_id, block_type, page, content, created_at,
                 page_range_start, page_range_end, llm_cleaned_content, 
                 extraction_metadata, chunk_index, overlap_with)
                VALUES (:id, :doc_id, :block_type, :page, :content, :created_at,
                        :page_range_start, :page_range_end, :llm_cleaned_content,
                        :extraction_metadata, :chunk_index, :overlap_with)
            """), {
                "id": block_id,
                "doc_id": data["doc_id"],
                "block_type": data.get("block_type", "text"),
                "page": data.get("page", 0),
                "content": content,
                "created_at": datetime.now(UTC).isoformat(),
                "page_range_start": data.get("page_range_start"),
                "page_range_end": data.get("page_range_end"),
                "llm_cleaned_content": llm_cleaned,
                "extraction_metadata": json.dumps(data.get("extraction_metadata")) if data.get("extraction_metadata") else None,
                "chunk_index": data.get("chunk_index", 0),
                "overlap_with": json.dumps(data.get("overlap_with")) if data.get("overlap_with") else None,
            })
            await s.commit()
        return block_id

    async def get_blocks(self, doc_id: str, page: Optional[int] = None) -> list[dict[str, Any]]:
        """Get blocks for a document, optionally filtered by page."""
        if page is not None:
            return await self.execute_query(
                "SELECT * FROM blocks WHERE doc_id = ? AND page = ? ORDER BY chunk_index",
                [doc_id, page]
            )
        return await self.execute_query(
            "SELECT * FROM blocks WHERE doc_id = ? ORDER BY page, chunk_index",
            [doc_id]
        )

    # ══════════════════════════════════════════════════════════════════════════
    # KNOWLEDGE BASE
    # ══════════════════════════════════════════════════════════════════════════

    async def insert_kb_item(self, data: dict) -> str:
        """Create a knowledge base item."""
        kb_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO knowledge_base_items 
                (id, title, item_type, course_id, file_path, filename, total_pages,
                 processing_status, paired_with_id, metadata, uploaded_at)
                VALUES (:id, :title, :item_type, :course_id, :file_path, :filename, :total_pages,
                        :processing_status, :paired_with_id, :metadata, :uploaded_at)
            """), {
                "id": kb_id,
                "title": data["title"],
                "item_type": data.get("item_type", "textbook"),
                "course_id": data.get("course_id"),
                "file_path": data["file_path"],
                "filename": data["filename"],
                "total_pages": data.get("total_pages", 0),
                "processing_status": data.get("processing_status", "pending"),
                "paired_with_id": data.get("paired_with_id"),
                "metadata": json.dumps(data.get("metadata")) if data.get("metadata") else None,
                "uploaded_at": datetime.now(UTC).isoformat(),
            })
            await s.commit()
        return kb_id

    async def list_kb_items(self, course_id: Optional[str] = None, item_type: Optional[str] = None) -> list[dict[str, Any]]:
        """List knowledge base items."""
        if course_id and item_type:
            return await self.execute_query(
                "SELECT * FROM knowledge_base_items WHERE course_id = ? AND item_type = ? ORDER BY title",
                [course_id, item_type]
            )
        elif course_id:
            return await self.execute_query(
                "SELECT * FROM knowledge_base_items WHERE course_id = ? ORDER BY title",
                [course_id]
            )
        elif item_type:
            return await self.execute_query(
                "SELECT * FROM knowledge_base_items WHERE item_type = ? ORDER BY title",
                [item_type]
            )
        return await self.execute_query("SELECT * FROM knowledge_base_items ORDER BY title")

    async def insert_kb_block(self, data: dict) -> str:
        """Create a knowledge base block."""
        block_id = str(uuid.uuid4())
        content = data["content"]
        if not isinstance(content, str):
            content = json.dumps(content)
        
        cleaned_content = data.get("cleaned_content")
        if cleaned_content and not isinstance(cleaned_content, str):
            cleaned_content = json.dumps(cleaned_content)
        
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO kb_blocks 
                (id, kb_item_id, block_type, page, content, cleaned_content,
                 question_number, topic, embedding_id, metadata, created_at)
                VALUES (:id, :kb_item_id, :block_type, :page, :content, :cleaned_content,
                        :question_number, :topic, :embedding_id, :metadata, :created_at)
            """), {
                "id": block_id,
                "kb_item_id": data["kb_item_id"],
                "block_type": data.get("block_type", "text"),
                "page": data.get("page", 0),
                "content": content,
                "cleaned_content": cleaned_content,
                "question_number": data.get("question_number"),
                "topic": data.get("topic"),
                "embedding_id": data.get("embedding_id"),
                "metadata": json.dumps(data.get("metadata")) if data.get("metadata") else None,
                "created_at": datetime.now(UTC).isoformat(),
            })
            await s.commit()
        return block_id

    async def insert_question_solution_pair(self, data: dict) -> str:
        """Link a question with its solution."""
        pair_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO question_solution_pairs 
                (id, question_block_id, solution_block_id, question_number, topic, difficulty, confidence_score, created_at)
                VALUES (:id, :question_block_id, :solution_block_id, :question_number, :topic, :difficulty, :confidence_score, :created_at)
            """), {
                "id": pair_id,
                "question_block_id": data["question_block_id"],
                "solution_block_id": data.get("solution_block_id"),
                "question_number": data.get("question_number"),
                "topic": data.get("topic"),
                "difficulty": data.get("difficulty"),
                "confidence_score": data.get("confidence_score", 0.5),
                "created_at": datetime.now(UTC).isoformat(),
            })
            await s.commit()
        return pair_id

    # ══════════════════════════════════════════════════════════════════════════
    # QUESTIONS (Enhanced)
    # ══════════════════════════════════════════════════════════════════════════

    async def insert_question(self, data: dict) -> str:
        """Create a question with enhanced fields."""
        q_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO questions 
                (id, doc_id, text, topic, year, prediction_score, source_type,
                 difficulty, linked_solution_id, frequency_score, importance_score)
                VALUES (:id, :doc_id, :text, :topic, :year, :prediction_score, :source_type,
                        :difficulty, :linked_solution_id, :frequency_score, :importance_score)
            """), {
                "id": q_id,
                "doc_id": data["doc_id"],
                "text": data["text"],
                "topic": data.get("topic"),
                "year": data.get("year"),
                "prediction_score": data.get("prediction_score", 0.0),
                "source_type": data.get("source_type", "past_paper"),
                "difficulty": data.get("difficulty"),
                "linked_solution_id": data.get("linked_solution_id"),
                "frequency_score": data.get("frequency_score", 0.0),
                "importance_score": data.get("importance_score", 0.0),
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

    # ══════════════════════════════════════════════════════════════════════════
    # STUDY SESSIONS
    # ══════════════════════════════════════════════════════════════════════════

    async def insert_study_session(self, data: dict) -> str:
        """Create a study session."""
        session_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO study_sessions 
                (id, course_id, doc_id, started_at, pages_viewed, topics_covered, metadata)
                VALUES (:id, :course_id, :doc_id, :started_at, :pages_viewed, :topics_covered, :metadata)
            """), {
                "id": session_id,
                "course_id": data.get("course_id"),
                "doc_id": data.get("doc_id"),
                "started_at": datetime.now(UTC).isoformat(),
                "pages_viewed": json.dumps(data.get("pages_viewed", [])),
                "topics_covered": json.dumps(data.get("topics_covered", [])),
                "metadata": json.dumps(data.get("metadata")) if data.get("metadata") else None,
            })
            await s.commit()
        return session_id

    async def end_study_session(self, session_id: str, duration_seconds: int) -> None:
        """End a study session."""
        async with get_async_session() as s:
            await s.execute(text("""
                UPDATE study_sessions 
                SET ended_at = :ended_at, duration_seconds = :duration
                WHERE id = :id
            """), {
                "ended_at": datetime.now(UTC).isoformat(),
                "duration": duration_seconds,
                "id": session_id
            })
            await s.commit()

    async def get_current_study_session(self, course_id: Optional[str] = None) -> Optional[dict[str, Any]]:
        """Get the most recent active study session."""
        if course_id:
            results = await self.execute_query(
                "SELECT * FROM study_sessions WHERE course_id = ? AND ended_at IS NULL ORDER BY started_at DESC LIMIT 1",
                [course_id]
            )
        else:
            results = await self.execute_query(
                "SELECT * FROM study_sessions WHERE ended_at IS NULL ORDER BY started_at DESC LIMIT 1"
            )
        return results[0] if results else None

    async def insert_explanation(self, data: dict) -> str:
        """Store an AI explanation."""
        explanation_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO explanations 
                (id, session_id, doc_id, page_number, query, response, context_blocks,
                 selected_text, model_used, confidence, citations, created_at)
                VALUES (:id, :session_id, :doc_id, :page_number, :query, :response, :context_blocks,
                        :selected_text, :model_used, :confidence, :citations, :created_at)
            """), {
                "id": explanation_id,
                "session_id": data.get("session_id"),
                "doc_id": data.get("doc_id"),
                "page_number": data.get("page_number"),
                "query": data["query"],
                "response": data["response"],
                "context_blocks": json.dumps(data.get("context_blocks", [])),
                "selected_text": data.get("selected_text"),
                "model_used": data.get("model_used"),
                "confidence": data.get("confidence"),
                "citations": json.dumps(data.get("citations", [])),
                "created_at": datetime.now(UTC).isoformat(),
            })
            await s.commit()
        return explanation_id

    async def insert_conversation(self, data: dict) -> str:
        """Store a conversation message."""
        conv_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO conversation_history 
                (id, session_id, role, content, doc_context, timestamp, metadata)
                VALUES (:id, :session_id, :role, :content, :doc_context, :timestamp, :metadata)
            """), {
                "id": conv_id,
                "session_id": data.get("session_id"),
                "role": data["role"],
                "content": data["content"],
                "doc_context": json.dumps(data.get("doc_context")) if data.get("doc_context") else None,
                "timestamp": datetime.now(UTC).isoformat(),
                "metadata": json.dumps(data.get("metadata")) if data.get("metadata") else None,
            })
            await s.commit()
        return conv_id

    async def get_conversation_history(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Get conversation history for a session."""
        return await self.execute_query(
            "SELECT * FROM conversation_history WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            [session_id, limit]
        )

    # ══════════════════════════════════════════════════════════════════════════
    # TOPIC ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════

    async def upsert_topic_analysis(self, data: dict) -> str:
        """Create or update topic analysis."""
        # First try to find existing
        results = await self.execute_query(
            "SELECT id FROM topic_analysis WHERE topic = ? AND course_id = ?",
            [data["topic"], data.get("course_id")]
        )
        
        if results:
            # Update existing
            topic_id = results[0]["id"]
            async with get_async_session() as s:
                await s.execute(text("""
                    UPDATE topic_analysis 
                    SET frequency_count = :freq, question_count = :qcount, 
                        kb_coverage = :coverage, importance_score = :importance,
                        last_seen_year = :year, metadata = :metadata, updated_at = :updated
                    WHERE id = :id
                """), {
                    "freq": data.get("frequency_count", 0),
                    "qcount": data.get("question_count", 0),
                    "coverage": data.get("kb_coverage", 0.0),
                    "importance": data.get("importance_score", 0.0),
                    "year": data.get("last_seen_year"),
                    "metadata": json.dumps(data.get("metadata")) if data.get("metadata") else None,
                    "updated": datetime.now(UTC).isoformat(),
                    "id": topic_id
                })
                await s.commit()
        else:
            # Insert new
            topic_id = str(uuid.uuid4())
            async with get_async_session() as s:
                await s.execute(text("""
                    INSERT INTO topic_analysis 
                    (id, topic, course_id, frequency_count, question_count, kb_coverage,
                     importance_score, last_seen_year, metadata, updated_at)
                    VALUES (:id, :topic, :course_id, :freq, :qcount, :coverage,
                            :importance, :year, :metadata, :updated)
                """), {
                    "id": topic_id,
                    "topic": data["topic"],
                    "course_id": data.get("course_id"),
                    "freq": data.get("frequency_count", 0),
                    "qcount": data.get("question_count", 0),
                    "coverage": data.get("kb_coverage", 0.0),
                    "importance": data.get("importance_score", 0.0),
                    "year": data.get("last_seen_year"),
                    "metadata": json.dumps(data.get("metadata")) if data.get("metadata") else None,
                    "updated": datetime.now(UTC).isoformat(),
                })
                await s.commit()
        
        return topic_id

    async def get_top_topics(self, course_id: Optional[str] = None, limit: int = 20) -> list[dict[str, Any]]:
        """Get most important topics."""
        if course_id:
            return await self.execute_query(
                "SELECT * FROM topic_analysis WHERE course_id = ? ORDER BY importance_score DESC LIMIT ?",
                [course_id, limit]
            )
        return await self.execute_query(
            "SELECT * FROM topic_analysis ORDER BY importance_score DESC LIMIT ?",
            [limit]
        )

    # ══════════════════════════════════════════════════════════════════════════
    # PROCESSING JOBS
    # ══════════════════════════════════════════════════════════════════════════

    async def insert_processing_job(self, data: dict) -> str:
        """Create a processing job."""
        job_id = str(uuid.uuid4())
        async with get_async_session() as s:
            await s.execute(text("""
                INSERT INTO processing_jobs 
                (id, job_type, target_id, status, progress, metadata, created_at)
                VALUES (:id, :job_type, :target_id, :status, :progress, :metadata, :created_at)
            """), {
                "id": job_id,
                "job_type": data["job_type"],
                "target_id": data["target_id"],
                "status": data.get("status", "pending"),
                "progress": data.get("progress", 0.0),
                "metadata": json.dumps(data.get("metadata")) if data.get("metadata") else None,
                "created_at": datetime.now(UTC).isoformat(),
            })
            await s.commit()
        return job_id

    async def update_processing_job(self, job_id: str, status: str, progress: float = None, error: str = None) -> None:
        """Update processing job status."""
        async with get_async_session() as s:
            updates = {"status": status, "id": job_id}
            sql_parts = ["UPDATE processing_jobs SET status = :status"]
            
            if progress is not None:
                sql_parts.append("progress = :progress")
                updates["progress"] = progress
            
            if error:
                sql_parts.append("error_message = :error")
                updates["error"] = error
            
            if status == "running" and not updates.get("started_at"):
                sql_parts.append("started_at = :started")
                updates["started"] = datetime.now(UTC).isoformat()
            
            if status in ("completed", "failed"):
                sql_parts.append("completed_at = :completed")
                updates["completed"] = datetime.now(UTC).isoformat()
            
            sql = ", ".join(sql_parts[1:])
            await s.execute(text(f"{sql_parts[0]}, {sql} WHERE id = :id"), updates)
            await s.commit()

    # ══════════════════════════════════════════════════════════════════════════
    # UTILITY
    # ══════════════════════════════════════════════════════════════════════════

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