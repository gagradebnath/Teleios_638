"""
main.py — τέλειος Teleios application entry point.

Lifespan order:
  1. Load all JSON configs
  2. Initialise SQLite/PostgreSQL via init_db()
  3. Build VectorStoreService
  4. Build tool registry (adapter=None for tools that need it)
  5. Build ModelAdapter from config
  6. Inject adapter into vector_search + document_retrieval tools
  7. Build OrchestratorAgent
  8. Mount gateway router
  9. Yield (app is live)
 10. close_db() on shutdown
"""
from __future__ import annotations

import json
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


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_cfg    = _cfg("app.json")
    model_cfg  = _cfg("models.json")
    agents_cfg = _cfg("agents.json")
    tools_cfg  = _cfg("tools.json")
    pred_cfg   = _cfg("prediction.json")

    # 1. Database
    from db.session import init_db, close_db
    db_url = app_cfg.get("storage", {}).get("db_url", "sqlite+aiosqlite:///./data/teleios.db")
    await init_db(db_url)

    # 2. Vector store
    from services.vector_store import VectorStoreService
    vector_store = VectorStoreService(app_cfg.get("storage", {}))

    # 3. Tool registry (adapter slots left as None)
    from tools.registry import build_tool_registry
    tools = build_tool_registry(tools_cfg, app_cfg, vector_store)

    # 4. Model adapter
    from adapters import get_adapter
    adapter = get_adapter(model_cfg)

    # 5. Inject adapter into tools that need it
    tools["vector_search"].set_adapter(adapter)
    tools["document_retrieval"].set_adapter(adapter)

    # 6. Orchestrator
    from agents.orchestrator import Orchestrator
    orchestrator = Orchestrator(
        tools_registry=tools,
        adapter=adapter,
    )
    app.state.orchestrator = orchestrator

    logger.info("app.ready", version=app_cfg.get("version", "1.0.0"))
    yield

    # Shutdown
    await close_db()
    logger.info("app.shutdown")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="τέλειος Teleios",
    version="1.0.0",
    lifespan=lifespan,
)

app_cfg_for_cors = _cfg("app.json")
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_cfg_for_cors.get("gateway", {}).get("cors_origins", ["http://localhost:3000"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────

# Import and mount the gateway router
from gateway.router import router as gateway_router
app.include_router(gateway_router, prefix="", tags=[])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)