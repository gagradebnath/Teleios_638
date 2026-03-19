"""services/file_system_service.py — File system hierarchy management.

Provides Google Drive-like file/folder organization with:
- Hierarchical folder structure
- Path resolution and validation
- Course assignment
- File metadata tracking
"""
from __future__ import annotations
import os
from typing import Optional
from pathlib import Path

import structlog

logger = structlog.get_logger()


class FileSystemService:
    """Manage hierarchical file/folder structure."""

    def __init__(self, sql_store, upload_dir: str = "./data/uploads"):
        self.sql = sql_store
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None,
        course_id: Optional[str] = None
    ) -> dict:
        """Create a new folder."""
        # Build path
        if parent_id:
            parent = await self.sql.get_file_system_node(parent_id)
            if not parent:
                raise ValueError(f"Parent folder not found: {parent_id}")
            if parent["node_type"] != "folder":
                raise ValueError("Parent must be a folder")
            path = f"{parent['path']}/{name}"
        else:
            path = f"/{name}"

        # Create in database
        node_id = await self.sql.insert_file_system_node({
            "name": name,
            "node_type": "folder",
            "parent_id": parent_id,
            "course_id": course_id,
            "path": path,
            "size_bytes": 0,
        })

        logger.info("folder.created", node_id=node_id, path=path)
        return {
            "id": node_id,
            "name": name,
            "path": path,
            "node_type": "folder",
            "parent_id": parent_id,
            "course_id": course_id,
        }

    async def create_file_node(
        self,
        name: str,
        file_path: str,
        size_bytes: int,
        mime_type: str,
        parent_id: Optional[str] = None,
        course_id: Optional[str] = None
    ) -> dict:
        """Create a file node (doesn't upload the actual file, just creates the metadata)."""
        # Build path
        if parent_id:
            parent = await self.sql.get_file_system_node(parent_id)
            if not parent:
                raise ValueError(f"Parent folder not found: {parent_id}")
            path = f"{parent['path']}/{name}"
        else:
            path = f"/{name}"

        # Create in database
        node_id = await self.sql.insert_file_system_node({
            "name": name,
            "node_type": "file",
            "parent_id": parent_id,
            "course_id": course_id,
            "path": path,
            "size_bytes": size_bytes,
            "mime_type": mime_type,
        })

        logger.info("file.node.created", node_id=node_id, path=path, size=size_bytes)
        return {
            "id": node_id,
            "name": name,
            "path": path,
            "node_type": "file",
            "parent_id": parent_id,
            "course_id": course_id,
            "file_path": file_path,
            "size_bytes": size_bytes,
            "mime_type": mime_type,
        }

    async def list_folder_contents(
        self,
        parent_id: Optional[str] = None,
        course_id: Optional[str] = None
    ) -> list[dict]:
        """List files and folders in a directory."""
        nodes = await self.sql.list_file_system_nodes(parent_id=parent_id, course_id=course_id)
        return nodes

    async def get_node(self, node_id: str) -> Optional[dict]:
        """Get a single file/folder node."""
        return await self.sql.get_file_system_node(node_id)

    async def get_node_path(self, node_id: str) -> list[dict]:
        """Get the breadcrumb path from root to this node."""
        path = []
        current_id = node_id

        while current_id:
            node = await self.sql.get_file_system_node(current_id)
            if not node:
                break
            path.insert(0, {
                "id": node["id"],
                "name": node["name"],
                "node_type": node["node_type"]
            })
            current_id = node.get("parent_id")

        return path

    async def delete_node(self, node_id: str) -> None:
        """Delete a file or folder (cascades to children)."""
        node = await self.sql.get_file_system_node(node_id)
        if not node:
            raise ValueError(f"Node not found: {node_id}")

        # TODO: Delete physical files if needed
        await self.sql.delete_file_system_node(node_id)
        logger.info("node.deleted", node_id=node_id, path=node["path"])

    async def move_node(self, node_id: str, new_parent_id: Optional[str] = None) -> dict:
        """Move a file/folder to a different parent."""
        # This would require updating the node and all its children's paths
        # For now, we'll leave this as a TODO
        raise NotImplementedError("Move operation not yet implemented")

    async def assign_to_course(self, node_id: str, course_id: str) -> None:
        """Assign a file/folder to a course."""
        # This would update the course_id field
        raise NotImplementedError("Course assignment not yet implemented")

    def get_physical_path(self, course_id: str, file_id: str) -> Path:
        """Get the physical file path for storage."""
        course_dir = self.upload_dir / course_id
        course_dir.mkdir(parents=True, exist_ok=True)
        return course_dir / file_id

    async def save_file(self, file_bytes: bytes, course_id: str, file_id: str) -> str:
        """Save a file to disk and return the path."""
        file_path = self.get_physical_path(course_id, file_id)
        
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        
        logger.info("file.saved", path=str(file_path), size=len(file_bytes))
        return str(file_path)
