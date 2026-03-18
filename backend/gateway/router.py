"""
gateway/router.py — FastAPI route handlers.

All routes delegate to app.state.orchestrator.run({intent, ...payload}).
Validation is handled by Pydantic schemas (auto-applied via type hints).
File uploads use FastAPI's UploadFile.
"""
from __future__ import annotations

from fastapi import APIRouter, Request, UploadFile, File, HTTPException

from gateway.schemas import (
    ExplainRequest,  ExplainResponse,
    PredictRequest,  PredictResponse,
    ExecuteRequest,  ExecuteResponse,
    AnalyzeRequest,  QuestionAnalysisResponse,
    IngestResponse,  HealthResponse,
)

import structlog

logger = structlog.get_logger()

router = APIRouter()


def _orch(request: Request):
    """Helper — pull orchestrator off app state."""
    return request.app.state.orchestrator


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