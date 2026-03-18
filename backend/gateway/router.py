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

    result = await _orch(request).run({
        "intent":    "ingest",
        "pdf_bytes": pdf_bytes,
        "filename":  file.filename or "upload.pdf",
    })

    if result.get("status") == "failed":
        raise HTTPException(status_code=500, detail=result.get("error", "Ingestion failed."))

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