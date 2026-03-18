"""
Test script to verify all backend imports work correctly.
Run this before starting the server to catch import errors early.

Usage:
    python test_imports.py
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all critical imports."""
    errors = []
    
    print("Testing backend imports...\n")
    
    # 1. Database layer
    print("1. Testing database layer...")
    try:
        from db.session import init_db, close_db, get_async_session
        from db.models.models import Document, Block, Question
        print("   ✅ Database layer imports OK")
    except Exception as e:
        errors.append(f"   ❌ Database layer: {e}")
        print(errors[-1])
    
    # 2. Services layer
    print("2. Testing services layer...")
    try:
        from services.vector_store import VectorStoreService
        from services.sql_store import SQLStoreService
        from services.ocr_service import OCRService
        from services.sandbox_service import SandboxService
        print("   ✅ Services layer imports OK")
    except Exception as e:
        errors.append(f"   ❌ Services layer: {e}")
        print(errors[-1])
    
    # 3. Adapters layer
    print("3. Testing adapters layer...")
    try:
        from adapters import get_adapter, ModelAdapter
        from adapters.ollama_adapter import OllamaAdapter
        from adapters.openai_adapter import OpenAIAdapter
        from adapters.anthropic_adapter import AnthropicAdapter
        from adapters.vllm_adapter import VLLMAdapter
        print("   ✅ Adapters layer imports OK")
    except Exception as e:
        errors.append(f"   ❌ Adapters layer: {e}")
        print(errors[-1])
    
    # 4. Tools layer
    print("4. Testing tools layer...")
    try:
        from tools.base_tool import BaseTool, ToolDefinition
        from tools.vector_search import VectorSearchTool
        from tools.sql_query import SQLQueryTool
        from tools.python_exec import PythonExecTool
        from tools.document_retrieval import DocumentRetrievalTool
        from tools.stats_analysis import StatsAnalysisTool
        from tools.registry.registry import build_tool_registry
        print("   ✅ Tools layer imports OK")
    except Exception as e:
        errors.append(f"   ❌ Tools layer: {e}")
        print(errors[-1])
    
    # 5. Agents layer
    print("5. Testing agents layer...")
    try:
        from agents.base_agent import BaseAgent
        from agents.document_agent import DocumentAgent
        from agents.retrieval_agent import RetrievalAgent
        from agents.qa_agent import QAAgent
        from agents.explanation_agent import ExplanationAgent
        from agents.execution_agent import ExecutionAgent
        from agents.prediction_agent import PredictionAgent
        from agents.orchestrator import Orchestrator
        print("   ✅ Agents layer imports OK")
    except Exception as e:
        errors.append(f"   ❌ Agents layer: {e}")
        print(errors[-1])
    
    # 6. Gateway layer
    print("6. Testing gateway layer...")
    try:
        from gateway.router import router
        from gateway.schemas import (
            ExplainRequest, ExplainResponse,
            PredictRequest, PredictResponse,
            ExecuteRequest, ExecuteResponse,
            IngestResponse, HealthResponse,
        )
        from gateway.middleware import LoggingMiddleware
        print("   ✅ Gateway layer imports OK")
    except Exception as e:
        errors.append(f"   ❌ Gateway layer: {e}")
        print(errors[-1])
    
    # 7. Main application
    print("7. Testing main application...")
    try:
        import main
        print("   ✅ Main application imports OK")
    except Exception as e:
        errors.append(f"   ❌ Main application: {e}")
        print(errors[-1])
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print(f"❌ FAILED: {len(errors)} import error(s) found:\n")
        for error in errors:
            print(error)
        return False
    else:
        print("✅ SUCCESS: All imports working correctly!")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
