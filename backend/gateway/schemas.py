"""
gateway/schemas.py — Pydantic request + response schemas for all endpoints.

Every route in router.py uses these for automatic validation and OpenAPI docs.
Block content schemas mirror what OCRService produces and what the DB stores.
"""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Block content schemas ─────────────────────────────────────────────────────

class TextBlockContent(BaseModel):
    text: str
    bbox: list[float] = Field(default_factory=list)


class EquationBlockContent(BaseModel):
    image_b64:   str
    description: Optional[str] = None


class FigureBlockContent(BaseModel):
    image_b64:   str
    description: Optional[str] = None


class TableBlockContent(BaseModel):
    rows:    list[list[str]]
    caption: Optional[str] = None


# ── /ingest ───────────────────────────────────────────────────────────────────

class IngestResponse(BaseModel):
    doc_id:           str
    title:            str
    filename:         str
    pages:            int
    blocks_extracted: int
    block_types:      dict[str, int]   # {"text": 14, "equation": 3, ...}
    status:           str              # "success" | "failed"
    error:            Optional[str] = None


# ── /explain ──────────────────────────────────────────────────────────────────

class ExplainRequest(BaseModel):
    query:           str
    doc_id:          Optional[str] = None
    highlighted_text: Optional[str] = None


class Citation(BaseModel):
    doc_id:  str
    title:   str
    page:    int
    excerpt: str


class ExplainResponse(BaseModel):
    answer:      str
    citations:   list[Citation] = Field(default_factory=list)
    confidence:  str            # "high" | "medium" | "low" | "insufficient_context"
    context_used: list[str] = Field(default_factory=list)


# ── /predict ──────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    doc_ids: list[str]
    subject: Optional[str] = None


class PredictedQuestion(BaseModel):
    id:               str
    text:             str
    topic:            Optional[str]
    year:             Optional[int]
    prediction_score: float


class PredictResponse(BaseModel):
    questions:    list[PredictedQuestion]
    total_scored: int
    weights_used: dict[str, float]


# ── /execute ──────────────────────────────────────────────────────────────────

class ExecuteRequest(BaseModel):
    code:    Optional[str] = None
    context: Optional[str] = None   # natural-language prompt → model generates code


class ExecuteResponse(BaseModel):
    stdout:             str
    figures:            list[str] = Field(default_factory=list)   # base64 PNGs
    error:              Optional[str] = None
    computation_verified: bool = False


# ── /analyze ──────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    doc_ids:  list[str]
    group_by: str = "topic"   # "topic" | "year" | "type"


class TopicStats(BaseModel):
    topic:     str
    count:     int
    avg_score: float


class QuestionAnalysisResponse(BaseModel):
    doc_ids:    list[str]
    group_by:   str
    stats:      list[TopicStats]
    total:      int


# ── /health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status:   str
    version:  str
    platform: str