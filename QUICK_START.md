# τέλειος Quick Start Guide

> **Get your AI study assistant running in 5 minutes!**

---

## Prerequisites

- **Python 3.10+** (check: `python --version`)
- **Node.js 16+** (check: `node --version`)
- **Git** (optional, for cloning)

---

## Step 1: Pre-flight Check (2 minutes)

### Run the pre-flight checker:
```bash
cd backend
python preflight.py
```

**Expected output:**
```
✅ ALL CHECKS PASSED!
You can now start the server
```

If checks fail, install dependencies:
```bash
pip install -r requirements.txt
```

---

## Step 2: Start Backend (1 minute)

### Option A: Using uvicorn directly
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8005
```

### Option B: Using the startup script
```bash
cd backend
python -m uvicorn main:app --reload --port 8005
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8005
INFO:     Application startup complete
```

**Test it works:**
```bash
curl http://localhost:8005/health
```

Expected response:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "platform": "teleios"
}
```

---

## Step 3: Start Frontend (2 minutes)

### In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

**Expected output:**
```
  VITE v4.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

**Open in browser:**
```
http://localhost:5173
```

---

## Step 4: Verify It Works (1 minute)

### You should see:
1. ✅ React app loads with 4 tabs (Chat, Ingest, Predict, Execute)
2. ✅ Left panel shows "No document loaded"
3. ✅ Right panel shows selected tab

### Quick tests:
1. **Execute Panel** — Try running Python code:
   ```python
   print("Hello from τέλειος!")
   result = 2 + 2
   print(f"2 + 2 = {result}")
   ```

2. **Ingest Panel** — Drag & drop a PDF to upload

3. **Chat Panel** — Ask a question after uploading

---

## Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Fix:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

---

### Frontend won't start

**Error:** `npm: command not found`

**Fix:** Install Node.js from https://nodejs.org/

**Error:** `ECONNREFUSED` when uploading files

**Fix:** Make sure backend is running on port 8005

---

### Can't connect to Ollama

**Error:** `Connection refused to localhost:11434`

**Fix:** Either:
1. Install and start Ollama: https://ollama.ai/
2. OR use OpenAI by setting: `OPENAI_API_KEY=sk-...`

**Check current model provider:**
```bash
cat config/models.json | grep active_provider
```

---

## Configuration

### Change model provider

Edit `config/models.json`:
```json
{
  "active_provider": "ollama"  // Change to: "openai", "anthropic", "vllm"
}
```

### Change database location

Edit `config/app.json`:
```json
{
  "storage": {
    "db_url": "sqlite+aiosqlite:///./data/teleios.db"
  }
}
```

Or set environment variable:
```bash
export DB_URL="postgresql+asyncpg://user:pass@localhost/teleios"
```

### Change API port

Edit `config/gateway.json`:
```json
{
  "server": {
    "port": 8005  // Change to your preferred port
  }
}
```

---

## Advanced Setup

### Using Docker Compose

```bash
docker-compose up -d
```

This starts:
- FastAPI backend (port 8005)
- ChromaDB vector store (port 8001)

### Using PostgreSQL instead of SQLite

1. Set environment variable:
   ```bash
   export DB_URL="postgresql+asyncpg://user:pass@localhost/teleios"
   ```

2. Run migrations:
   ```bash
   cd backend
   python -c "from db.session import init_db; import asyncio; asyncio.run(init_db())"
   ```

### Using ChromaDB

1. Start ChromaDB:
   ```bash
   docker run -p 8001:8000 chromadb/chroma
   ```

2. Backend will auto-connect (check config/app.json)

---

## Testing

### Run backend tests:
```bash
cd backend
python run_tests.py
```

### Run quick tests only:
```bash
python run_tests.py --quick
```

See `backend/TESTING.md` for details.

---

## What's Next?

1. **Upload a PDF** — Use the Ingest panel
2. **Ask questions** — Chat panel finds relevant content
3. **Generate study questions** — Predict panel analyzes topics
4. **Run Python code** — Execute panel with matplotlib support

---

## Getting Help

- **BUILD_PROGRESS.md** — Detailed build status and progress
- **AUDIT_REPORT.md** — Complete system audit and architecture
- **PLAN.md** — Full architecture and design document
- **backend/TESTING.md** — Testing guide

---

## Architecture at a Glance

```
Frontend (React + PDF.js)
    ↓
API Gateway (FastAPI)
    ↓
Orchestrator (Intent Routing)
    ↓
6 Specialized Agents
    ↓
5 MCP Tools
    ↓
4 Services (Vector, SQL, OCR, Sandbox)
    ↓
Storage (SQLite + ChromaDB)
```

**Total Lines of Code:** ~15,000  
**Config Files:** 9 JSON files  
**Test Coverage:** Import, Config, Basic Functionality

---

**Last Updated:** 2026-03-18 22:09 UTC  
**Version:** 1.0.0  
**Status:** ✅ Ready for Testing
