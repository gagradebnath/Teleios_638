"""services/course_service.py — Course management service.

Handles:
- Course CRUD operations
- Course-document associations
- Course statistics and summaries
"""
from __future__ import annotations
from typing import Optional

import structlog

logger = structlog.get_logger()


class CourseService:
    """Manage courses and their materials."""

    def __init__(self, sql_store):
        self.sql = sql_store

    async def create_course(
        self,
        name: str,
        code: Optional[str] = None,
        description: Optional[str] = None,
        color: str = "#3b82f6"
    ) -> dict:
        """Create a new course."""
        course_id = await self.sql.insert_course({
            "name": name,
            "code": code,
            "description": description,
            "color": color,
        })

        logger.info("course.created", course_id=course_id, name=name)
        return {
            "id": course_id,
            "name": name,
            "code": code,
            "description": description,
            "color": color,
        }

    async def list_courses(self) -> list[dict]:
        """Get all courses."""
        courses = await self.sql.list_courses()
        return courses

    async def get_course(self, course_id: str) -> Optional[dict]:
        """Get a single course."""
        return await self.sql.get_course(course_id)

    async def get_course_documents(self, course_id: str) -> list[dict]:
        """Get all documents for a course."""
        return await self.sql.list_documents(course_id=course_id)

    async def get_course_stats(self, course_id: str) -> dict:
        """Get statistics for a course."""
        documents = await self.sql.list_documents(course_id=course_id)
        
        # Count documents by type
        doc_types = {}
        total_pages = 0
        
        for doc in documents:
            doc_type = doc.get("doc_type", "unknown")
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            total_pages += doc.get("total_pages", 0)

        # Get knowledge base items
        kb_items = await self.sql.list_kb_items(course_id=course_id)
        
        # Get top topics
        topics = await self.sql.get_top_topics(course_id=course_id, limit=10)

        return {
            "course_id": course_id,
            "document_count": len(documents),
            "document_types": doc_types,
            "total_pages": total_pages,
            "kb_item_count": len(kb_items),
            "top_topics": [t["topic"] for t in topics[:5]],
        }

    async def delete_course(self, course_id: str) -> None:
        """Delete a course (this would cascade to related items)."""
        # For now, this is a TODO - requires careful cascade handling
        raise NotImplementedError("Course deletion not yet implemented")

    async def update_course(
        self,
        course_id: str,
        name: Optional[str] = None,
        code: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None
    ) -> dict:
        """Update course details."""
        # This would require an update method in sql_store
        raise NotImplementedError("Course update not yet implemented")
