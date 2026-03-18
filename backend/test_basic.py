"""
Basic functional tests for the τέλειος backend.
Tests core functionality without requiring external services.

Usage:
    python test_basic.py
"""
import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

CONFIG_DIR = Path(__file__).parent.parent / "config"

def load_config(name: str) -> dict:
    """Load a config file."""
    path = CONFIG_DIR / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


async def test_adapter_factory():
    """Test ModelAdapter factory."""
    print("Testing ModelAdapter factory...")
    
    try:
        from adapters import get_adapter
        
        models_cfg = load_config("models.json")
        if not models_cfg:
            print("   ⚠️  models.json not found, skipping")
            return True
        
        adapter = get_adapter(models_cfg)
        print(f"   ✅ Created adapter: {adapter.__class__.__name__}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


async def test_vector_store_init():
    """Test VectorStoreService initialization."""
    print("Testing VectorStoreService initialization...")
    
    try:
        from services.vector_store import VectorStoreService
        
        app_cfg = load_config("app.json")
        storage_cfg = app_cfg.get("storage", {})
        
        vector_store = VectorStoreService(storage_cfg)
        print(f"   ✅ VectorStore initialized (collection: {vector_store.collection_name})")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


async def test_sql_store_init():
    """Test SQLStoreService initialization."""
    print("Testing SQLStoreService initialization...")
    
    try:
        from services.sql_store import SQLStoreService
        
        sql_store = SQLStoreService()
        print(f"   ✅ SQLStore initialized")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


async def test_ocr_service_init():
    """Test OCRService initialization."""
    print("Testing OCRService initialization...")
    
    try:
        from services.ocr_service import OCRService
        
        app_cfg = load_config("app.json")
        ocr_cfg = app_cfg.get("ocr", {})
        
        ocr_service = OCRService(ocr_cfg)
        print(f"   ✅ OCRService initialized (engine: {ocr_service.engine})")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


async def test_sandbox_service_init():
    """Test SandboxService initialization."""
    print("Testing SandboxService initialization...")
    
    try:
        from services.sandbox_service import SandboxService
        
        app_cfg = load_config("app.json")
        sandbox_cfg = app_cfg.get("sandbox", {})
        
        sandbox = SandboxService(sandbox_cfg)
        print(f"   ✅ SandboxService initialized (timeout: {sandbox.default_timeout}s)")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


async def test_tool_registry():
    """Test tool registry building."""
    print("Testing tool registry...")
    
    try:
        from tools.registry.registry import build_tool_registry
        from services.vector_store import VectorStoreService
        
        app_cfg = load_config("app.json")
        tools_cfg = load_config("tools.json")
        agents_cfg = load_config("agents.json")
        
        vector_store = VectorStoreService(app_cfg.get("storage", {}))
        
        tools = build_tool_registry(tools_cfg, app_cfg, vector_store, agents_cfg)
        
        print(f"   ✅ Tool registry built with {len(tools)} tools:")
        for tool_name in tools:
            print(f"      - {tool_name}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


async def test_orchestrator_init():
    """Test Orchestrator initialization."""
    print("Testing Orchestrator initialization...")
    
    try:
        from agents.orchestrator import Orchestrator
        from tools.registry.registry import build_tool_registry
        from services.vector_store import VectorStoreService
        from adapters import get_adapter
        
        # Load configs
        app_cfg = load_config("app.json")
        models_cfg = load_config("models.json")
        tools_cfg = load_config("tools.json")
        agents_cfg = load_config("agents.json")
        
        # Build dependencies
        vector_store = VectorStoreService(app_cfg.get("storage", {}))
        tools = build_tool_registry(tools_cfg, app_cfg, vector_store, agents_cfg)
        adapter = get_adapter(models_cfg)
        
        # Inject adapter into tools that need it
        if "vector_search" in tools:
            tools["vector_search"].set_adapter(adapter)
        if "document_retrieval" in tools:
            tools["document_retrieval"].set_adapter(adapter)
        
        # Build orchestrator
        orchestrator = Orchestrator(
            tools_registry=tools,
            adapter=adapter,
            config=agents_cfg,
        )
        
        print(f"   ✅ Orchestrator initialized with {len(orchestrator.agents)} agents:")
        for agent_name in orchestrator.agents:
            print(f"      - {agent_name}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


async def test_sandbox_execution():
    """Test sandbox code execution."""
    print("Testing sandbox code execution...")
    
    try:
        from services.sandbox_service import SandboxService
        
        app_cfg = load_config("app.json")
        sandbox = SandboxService(app_cfg.get("sandbox", {}))
        
        # Test simple code
        code = "print('Hello from sandbox!')\nresult = 2 + 2\nprint(f'2 + 2 = {result}')"
        result = sandbox.execute(code, timeout=5)
        
        if result.get("error"):
            print(f"   ⚠️  Sandbox execution error: {result['error']}")
            return False
        
        stdout = result.get("stdout", "")
        if "Hello from sandbox!" in stdout and "2 + 2 = 4" in stdout:
            print(f"   ✅ Sandbox execution successful")
            print(f"      Output: {stdout.strip()}")
            return True
        else:
            print(f"   ⚠️  Unexpected output: {stdout}")
            return False
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


async def run_all_tests():
    """Run all basic tests."""
    print("="*60)
    print("τέλειος Backend Basic Tests")
    print("="*60 + "\n")
    
    tests = [
        ("Adapter Factory", test_adapter_factory),
        ("VectorStore Init", test_vector_store_init),
        ("SQLStore Init", test_sql_store_init),
        ("OCRService Init", test_ocr_service_init),
        ("SandboxService Init", test_sandbox_service_init),
        ("Tool Registry", test_tool_registry),
        ("Orchestrator Init", test_orchestrator_init),
        ("Sandbox Execution", test_sandbox_execution),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("="*60)
    print("Test Summary:")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        return True
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
