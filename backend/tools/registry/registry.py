"""
Tool Registry Builder
Instantiates all MCP tools and returns them as a named dict.
Called once during app lifespan in main.py.

Note: VectorSearchTool and DocumentRetrievalTool are built with adapter=None.
      main.py must call tool.set_adapter(adapter) on both after building the adapter.
"""
from __future__ import annotations

from services.vector_store import VectorStoreService
from services.sql_store import SQLStoreService
from services.sandbox_service import SandboxService
from services.ocr_service import OCRService

from tools.vector_search import VectorSearchTool
from tools.sql_query import SQLQueryTool
from tools.python_exec import PythonExecTool
from tools.document_retrieval import DocumentRetrievalTool
from tools.stats_analysis import StatsAnalysisTool


def build_tool_registry(
    tools_cfg: dict,
    app_cfg: dict,
    vector_store: VectorStoreService,
) -> dict:
    """
    Build and return the full tool registry.

    Args:
        tools_cfg   — parsed config/tools.json
        app_cfg     — parsed config/app.json
        vector_store — already-initialized VectorStoreService

    Returns:
        dict[str, BaseTool] — keyed by tool name matching tools.json
    """
    # ── Service instances ────────────────────────────────────────────────────
    sql_store = SQLStoreService()
    sandbox   = SandboxService(app_cfg.get("sandbox", {}))
    ocr       = OCRService(app_cfg.get("ocr", {}))

    # ── Tool instances ───────────────────────────────────────────────────────
    # adapter=None for tools that need it — injected by main.py after adapter creation
    vector_search_tool  = VectorSearchTool(adapter=None, vector_store=vector_store)
    sql_query_tool      = SQLQueryTool(sql_store=sql_store)
    python_exec_tool    = PythonExecTool(sandbox=sandbox)
    doc_retrieval_tool  = DocumentRetrievalTool(
        vector_store=vector_store,
        sql_store=sql_store,
        ocr_service=ocr,
    )
    stats_tool          = StatsAnalysisTool()

    registry = {
        "vector_search":     vector_search_tool,
        "sql_query":         sql_query_tool,
        "python_exec":       python_exec_tool,
        "document_retrieval": doc_retrieval_tool,
        "stats_analysis":    stats_tool,
    }

    return registry