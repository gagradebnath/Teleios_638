"""
gateway/router.py — FastAPI route handlers.

All routes delegate to app.state.orchestrator.run({intent, ...payload}).
Validation is handled by Pydantic schemas (auto-applied via type hints).
File uploads use FastAPI's UploadFile.

Enhanced with courses, file system, and knowledge base endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from typing import Optional

from gateway.schemas import (
    ExplainRequest,  ExplainResponse,
    PredictRequest,  PredictResponse,
    ExecuteRequest,  ExecuteResponse,
    AnalyzeRequest,  QuestionAnalysisResponse,
    IngestResponse,  HealthResponse,
    # New schemas
    CourseCreate, CourseResponse, CourseListResponse,
    FileSystemNodeResponse, FolderCreateRequest,
    FileSystemListResponse,
)

import structlog

logger = structlog.get_logger()

router = APIRouter()


def _orch(request: Request):
    """Helper — pull orchestrator off app state."""
    return request.app.state.orchestrator


def _sql(request: Request):
    """Helper — pull SQL store off app state."""
    return request.app.state.sql_store


def _fs(request: Request):
    """Helper — pull file system service off app state."""
    return request.app.state.file_system


def _course(request: Request):
    """Helper — pull course service off app state."""
    return request.app.state.course_service


# ── /health ───────────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health():
    return HealthResponse(status="ok", version="1.0.0", platform="teleios")


# ── /ingest ───────────────────────────────────────────────────────────────────

@router.post("/ingest", response_model=IngestResponse, tags=["documents"])
async def ingest(request: Request, file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    filename = file.filename or "upload.pdf"
    
    # Extract blocks from PDF using OCRService
    try:
        ocr_service = request.app.state.ocr_service
        blocks = await ocr_service.extract_blocks(pdf_bytes)
        if not blocks:
            logger.warning("ingest.no_blocks", filename=filename)
    except Exception as exc:
        logger.error("ingest.extraction_error", error=str(exc), filename=filename)
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(exc)}")
    
    # Count block types
    block_types = {}
    for block in blocks:
        btype = block.get("type", "unknown")
        block_types[btype] = block_types.get(btype, 0) + 1
    
    # Extract page count from blocks
    page_count = 0
    if blocks:
        page_count = max((block.get("page", 0) for block in blocks), default=0) + 1
    
    # Dispatch to orchestrator with proper parameters
    result = await _orch(request).run(
        intent="ingest",
        action="index",
        title=filename.replace(".pdf", ""),
        blocks=blocks,
    )
    
    # Check for errors (both "error" and "failed" status)
    if result.get("status") in ("error", "failed"):
        raise HTTPException(status_code=500, detail=result.get("error", "Ingestion failed."))
    
    # Enrich response with metadata
    result.update({
        "filename": filename,
        "pages": page_count,
        "blocks_extracted": len(blocks),
        "block_types": block_types,
        "status": "success" if result.get("status") == "ok" else result.get("status", "failed"),
    })
    
    return IngestResponse(**result)


# ── /explain ──────────────────────────────────────────────────────────────────

@router.post("/explain", response_model=ExplainResponse, tags=["qa"])
async def explain(request: Request, body: ExplainRequest):
    result = await _orch(request).run({
        "intent":           "explain",
        "query":            body.query,
        "doc_id":           body.doc_id,
        "highlighted_text": body.highlighted_text,
    })
    return ExplainResponse(**result)


# ── /predict ──────────────────────────────────────────────────────────────────

@router.post("/predict", response_model=PredictResponse, tags=["prediction"])
async def predict(request: Request, body: PredictRequest):
    result = await _orch(request).run({
        "intent":  "predict",
        "doc_ids": body.doc_ids,
        "subject": body.subject,
    })
    return PredictResponse(**result)


# ── /execute ──────────────────────────────────────────────────────────────────

@router.post("/execute", response_model=ExecuteResponse, tags=["execution"])
async def execute(request: Request, body: ExecuteRequest):
    if not body.code and not body.context:
        raise HTTPException(status_code=400, detail="Provide either 'code' or 'context'.")

    result = await _orch(request).run({
        "intent":  "execute",
        "code":    body.code,
        "context": body.context,
    })
    return ExecuteResponse(**result)


# ── /analyze ──────────────────────────────────────────────────────────────────

@router.post("/analyze", response_model=QuestionAnalysisResponse, tags=["qa"])
async def analyze(request: Request, body: AnalyzeRequest):
    result = await _orch(request).run({
        "intent":   "question",
        "doc_ids":  body.doc_ids,
        "group_by": body.group_by,
    })
    return QuestionAnalysisResponse(**result)


# ── /courses ──────────────────────────────────────────────────────────────────

@router.post("/courses", response_model=CourseResponse, tags=["courses"])
async def create_course(request: Request, body: CourseCreate):
    """Create a new course."""
    try:
        course = await _course(request).create_course(
            name=body.name,
            code=body.code,
            description=body.description,
            color=body.color or "#3b82f6"
        )
        return CourseResponse(**course)
    except Exception as exc:
        logger.error("courses.create_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/courses", response_model=CourseListResponse, tags=["courses"])
async def list_courses(request: Request):
    """List all courses."""
    try:
        courses = await _course(request).list_courses()
        return CourseListResponse(courses=courses)
    except Exception as exc:
        logger.error("courses.list_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/courses/{course_id}", response_model=CourseResponse, tags=["courses"])
async def get_course(request: Request, course_id: str):
    """Get a single course."""
    try:
        course = await _course(request).get_course(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return CourseResponse(**course)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("courses.get_error", error=str(exc), course_id=course_id)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/courses/{course_id}/stats", tags=["courses"])
async def get_course_stats(request: Request, course_id: str):
    """Get course statistics."""
    try:
        stats = await _course(request).get_course_stats(course_id)
        return stats
    except Exception as exc:
        logger.error("courses.stats_error", error=str(exc), course_id=course_id)
        raise HTTPException(status_code=500, detail=str(exc))


# ── /file-system ──────────────────────────────────────────────────────────────

@router.post("/file-system/folders", response_model=FileSystemNodeResponse, tags=["file-system"])
async def create_folder(request: Request, body: FolderCreateRequest):
    """Create a new folder."""
    try:
        folder = await _fs(request).create_folder(
            name=body.name,
            parent_id=body.parent_id,
            course_id=body.course_id
        )
        return FileSystemNodeResponse(**folder)
    except Exception as exc:
        logger.error("filesystem.create_folder_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/file-system/nodes", response_model=FileSystemListResponse, tags=["file-system"])
async def list_file_system_nodes(
    request: Request,
    parent_id: Optional[str] = None,
    course_id: Optional[str] = None
):
    """List files and folders."""
    try:
        nodes = await _fs(request).list_folder_contents(parent_id=parent_id, course_id=course_id)
        return FileSystemListResponse(nodes=nodes)
    except Exception as exc:
        logger.error("filesystem.list_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/file-system/nodes/{node_id}", response_model=FileSystemNodeResponse, tags=["file-system"])
async def get_file_system_node(request: Request, node_id: str):
    """Get a single file/folder node."""
    try:
        node = await _fs(request).get_node(node_id)
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        return FileSystemNodeResponse(**node)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("filesystem.get_error", error=str(exc), node_id=node_id)
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/file-system/nodes/{node_id}", tags=["file-system"])
async def delete_file_system_node(request: Request, node_id: str):
    """Delete a file or folder."""
    try:
        await _fs(request).delete_node(node_id)
        return {"status": "deleted", "node_id": node_id}
    except Exception as exc:
        logger.error("filesystem.delete_error", error=str(exc), node_id=node_id)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/file-system/nodes/{node_id}/path", tags=["file-system"])
async def get_node_path(request: Request, node_id: str):
    """Get breadcrumb path for a node."""
    try:
        path = await _fs(request).get_node_path(node_id)
        return {"node_id": node_id, "path": path}
    except Exception as exc:
        logger.error("filesystem.path_error", error=str(exc), node_id=node_id)
        raise HTTPException(status_code=500, detail=str(exc))


# ── /documents ────────────────────────────────────────────────────────────────

@router.get("/documents", tags=["documents"])
async def list_documents(request: Request, course_id: Optional[str] = None):
    """List all documents, optionally filtered by course."""
    try:
        documents = await _sql(request).list_documents(course_id=course_id)
        return {"documents": documents}
    except Exception as exc:
        logger.error("documents.list_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/documents/{doc_id}", tags=["documents"])
async def get_document(request: Request, doc_id: str):
    """Get a single document."""
    try:
        document = await _sql(request).get_document(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("documents.get_error", error=str(exc), doc_id=doc_id)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/documents/{doc_id}/pages", tags=["documents"])
async def get_document_pages(request: Request, doc_id: str):
    """Get all pages for a document."""
    try:
        pages = await _sql(request).get_document_pages(doc_id)
        return {"doc_id": doc_id, "pages": pages}
    except Exception as exc:
        logger.error("documents.pages_error", error=str(exc), doc_id=doc_id)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/documents/{doc_id}/blocks", tags=["documents"])
async def get_document_blocks(request: Request, doc_id: str, page: Optional[int] = None):
    """Get blocks for a document, optionally filtered by page."""
    try:
        blocks = await _sql(request).get_blocks(doc_id, page=page)
        return {"doc_id": doc_id, "page": page, "blocks": blocks}
    except Exception as exc:
        logger.error("documents.blocks_error", error=str(exc), doc_id=doc_id)
        raise HTTPException(status_code=500, detail=str(exc))