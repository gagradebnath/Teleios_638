# Testing Guide for τέλειος Backend

This directory contains comprehensive tests for the τέλειος backend system.

## Quick Start

### Run All Tests
```bash
python run_tests.py
```

### Run Quick Tests Only (imports + config)
```bash
python run_tests.py --quick
```

### Run with Verbose Output
```bash
python run_tests.py --verbose
```

---

## Test Suites

### 1. Import Tests (`test_imports.py`)
**Purpose:** Verify all Python modules can be imported without errors.

**Tests:**
- Database layer (models, session)
- Services layer (vector_store, sql_store, ocr_service, sandbox_service)
- Adapters layer (Ollama, OpenAI, Anthropic, VLLM)
- Tools layer (5 MCP tools + registry)
- Agents layer (6 agents + orchestrator)
- Gateway layer (router, schemas, middleware)
- Main application

**Run individually:**
```bash
python test_imports.py
```

**Expected Output:**
```
✅ SUCCESS: All imports working correctly!
```

---

### 2. Config Tests (`test_config.py`)
**Purpose:** Verify all JSON config files are valid and contain expected keys.

**Tests:**
- All 9 config files exist
- Valid JSON syntax
- Required keys present
- Configuration summary

**Run individually:**
```bash
python test_config.py
```

**Expected Output:**
```
✅ SUCCESS: All 9 config files valid!
```

---

### 3. Basic Functionality Tests (`test_basic.py`)
**Purpose:** Test core services and components initialize correctly.

**Tests:**
- ModelAdapter factory (creates correct adapter from config)
- VectorStoreService initialization
- SQLStoreService initialization
- OCRService initialization
- SandboxService initialization
- Tool registry building (5 tools)
- Orchestrator initialization (6 agents)
- Sandbox code execution (Python execution test)

**Run individually:**
```bash
python test_basic.py
```

**Expected Output:**
```
✅ ALL TESTS PASSED!
Results: 8/8 tests passed
```

---

## Test Requirements

### Minimal Requirements (for import + config tests)
- Python 3.10+
- All packages from `requirements.txt`

### Full Requirements (for basic functionality tests)
- Python 3.10+
- All packages from `requirements.txt`
- SQLite (included with Python)
- No external services required (ChromaDB, Ollama optional)

---

## Troubleshooting

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Config Errors

**Error:** `config file not found` or `Invalid JSON`

**Solution:**
1. Check `config/` directory exists
2. Verify all 9 config files are present:
   - app.json
   - models.json
   - agents.json
   - gateway.json
   - tools.json
   - prediction.json
   - server.json
   - adapters.json
   - frontend.json
3. Validate JSON syntax: `python -m json.tool config/app.json`

### Service Initialization Errors

**Error:** `ChromaDB connection failed`

**Solution:** This is expected if ChromaDB is not running. The system will fall back to in-memory storage.

**Error:** `RestrictedPython not installed`

**Solution:**
```bash
pip install RestrictedPython
```

---

## Integration Testing (Future)

After basic tests pass, proceed to integration testing:

1. **Start Backend Server**
   ```bash
   uvicorn main:app --reload --port 8005
   ```

2. **Test Health Endpoint**
   ```bash
   curl http://localhost:8005/health
   ```

3. **Test API Endpoints**
   - POST /ingest (upload PDF)
   - POST /explain (ask question)
   - POST /predict (generate questions)
   - POST /execute (run Python code)

4. **Test Frontend Integration**
   ```bash
   cd ../frontend
   npm run dev
   ```

---

## Test Coverage

### Current Coverage
- ✅ Import verification (100%)
- ✅ Config validation (100%)
- ✅ Service initialization (100%)
- ✅ Basic functionality (80%)
- ⏳ API endpoints (0% - manual testing)
- ⏳ E2E workflows (0% - manual testing)

### Future Tests (Phase 7)
- [ ] API endpoint unit tests
- [ ] Agent behavior tests
- [ ] Tool execution tests
- [ ] Database operations tests
- [ ] Vector search tests
- [ ] PDF ingestion tests
- [ ] Code execution tests

---

## CI/CD Integration

To integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Backend Tests
  run: |
    cd backend
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python run_tests.py --quick
```

---

## Test Output Files

Tests do not create output files by default. All results are printed to stdout.

For CI/CD, redirect output:
```bash
python run_tests.py > test_results.txt 2>&1
```

---

## Contact & Support

If tests fail unexpectedly:
1. Check BUILD_PROGRESS.md for known issues
2. Review AUDIT_REPORT.md for configuration details
3. Verify all dependencies installed: `pip list`
4. Check Python version: `python --version` (requires 3.10+)

---

**Last Updated:** 2026-03-18 22:09 UTC
