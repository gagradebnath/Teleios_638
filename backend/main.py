"""
main.py — τέλειος Teleios application entry point.

Lifespan order:
  1. Load all JSON configs
  2. Setup CORS middleware
  3. Initialise SQLite/PostgreSQL via init_db()
  4. Build VectorStoreService
  5. Build tool registry (adapter=None for tools that need it)
  6. Build ModelAdapter from config
  7. Inject adapter into vector_search + document_retrieval tools
  8. Build OrchestratorAgent
  9. Mount gateway router
  10. Yield (app is live)
  11. close_db() on shutdown
"""
from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import structlog

logger = structlog.get_logger()

BASE = Path(__file__).parent          # backend/
CONFIG = BASE.parent / "config"       # config/


def _cfg(name: str) -> dict:
    """Load a JSON config file from config/."""
    path = CONFIG / name
    if not path.exists():
        logger.warning("config.missing", file=name)
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _get_env_or_config(env_var: str, config_path: dict, default: str = None) -> str:
    """Get value from environment variable, config dict, or default.
    
    Args:
        env_var: Environment variable name
        config_path: Config value from JSON
        default: Default fallback value
    
    Returns:
        Resolved value string
    """
    return os.environ.get(env_var, config_path or default)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load all configs
    app_cfg     = _cfg("app.json")
    gateway_cfg = _cfg("gateway.json")
    models_cfg  = _cfg("models.json")
    agents_cfg  = _cfg("agents.json")
    tools_cfg   = _cfg("tools.json")
    pred_cfg    = _cfg("prediction.json")
    server_cfg  = _cfg("server.json")

    # Store all configs in app state for access in routes
    app.state.app_config = app_cfg
    app.state.gateway_config = gateway_cfg
    app.state.models_config = models_cfg
    app.state.agents_config = agents_cfg
    app.state.tools_config = tools_cfg
    app.state.server_config = server_cfg

    # 1. Database with env override
    from db.session import init_db, close_db
    db_url = _get_env_or_config(
        app_cfg.get("storage", {}).get("db_url_env", "DB_URL"),
        None,
        app_cfg.get("storage", {}).get("db_url", "sqlite+aiosqlite:///./data/teleios.db")
    )
    if os.environ.get("DB_URL"):
        db_url = os.environ.get("DB_URL")
    else:
        db_url = app_cfg.get("storage", {}).get("db_url", "sqlite+aiosqlite:///./data/teleios.db")
    
    await init_db(db_url)

    # 2. Vector store
    from services.vector_store import VectorStoreService
    vector_store = VectorStoreService(app_cfg.get("storage", {}))

    # 3. Tool registry (adapter slots left as None)
    from tools.registry.registry import build_tool_registry
    tools = build_tool_registry(tools_cfg, app_cfg, vector_store, agents_cfg)

    # 4. Model adapter
    from adapters import get_adapter
    adapter = get_adapter(models_cfg)

    # 5. Inject adapter into tools that need it
    tools["vector_search"].set_adapter(adapter)
    tools["document_retrieval"].set_adapter(adapter)

    # 6. OCR Service (for PDF extraction)
    from services.ocr_service import OCRService
    ocr_service = OCRService(app_cfg.get("ocr", {}))
    app.state.ocr_service = ocr_service

    # 7. Orchestrator
    from agents.orchestrator import Orchestrator
    orchestrator = Orchestrator(
        tools_registry=tools,
        adapter=adapter,
        config=agents_cfg,
    )
    app.state.orchestrator = orchestrator

    logger.info("app.ready", version=app_cfg.get("version", "1.0.0"))
    yield

    # Shutdown
    await close_db()
    logger.info("app.shutdown")


# ── App ───────────────────────────────────────────────────────────────────────

# Load gateway config
gateway_cfg = _cfg("gateway.json")
api_cfg = gateway_cfg.get("api", {})
server_cfg = gateway_cfg.get("server", {})
cors_cfg = gateway_cfg.get("cors", {})

app = FastAPI(
    title=api_cfg.get("title", "τέλειος Teleios"),
    version=api_cfg.get("version", "1.0.0"),
    description=api_cfg.get("description", "Multi-agent AI system for document analysis"),
    lifespan=lifespan,
)

# ── Mount CORS Middleware ─────────────────────────────────────────────────────

if cors_cfg.get("enabled", True):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_cfg.get("origins", ["http://localhost:3000", "http://localhost:5173"]),
        allow_credentials=cors_cfg.get("allow_credentials", True),
        allow_methods=cors_cfg.get("allow_methods", ["*"]),
        allow_headers=cors_cfg.get("allow_headers", ["*"]),
    )

# ── Mount Logging Middleware ──────────────────────────────────────────────────

from gateway.middleware import LoggingMiddleware
app.add_middleware(LoggingMiddleware)

# ── Root endpoint ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint returns API metadata."""
    return {
        "app": api_cfg.get("title", "τέλειος Teleios"),
        "version": api_cfg.get("version", "1.0.0"),
        "platform": api_cfg.get("platform", "teleios"),
        "docs": "/docs",
        "redoc": "/redoc",
    }


# ── Mount Gateway Router ──────────────────────────────────────────────────────

from gateway.router import router as gateway_router
app.include_router(gateway_router, prefix="", tags=["teleios"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)