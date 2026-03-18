"""
gateway — FastAPI/Pydantic layer for request/response handling and routing.

Exports:
  - router: FastAPI APIRouter with all endpoints
  - *Response: Pydantic response models for OpenAPI documentation
"""
from gateway.router import router
from gateway.schemas import (
    IngestResponse,
    ExplainResponse,
    PredictResponse,
    ExecuteResponse,
    QuestionAnalysisResponse,
    HealthResponse,
)

__all__ = [
    "router",
    "IngestResponse",
    "ExplainResponse",
    "PredictResponse",
    "ExecuteResponse",
    "QuestionAnalysisResponse",
    "HealthResponse",
]
