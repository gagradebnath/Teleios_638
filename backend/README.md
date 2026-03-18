# Teleios Backend — FastAPI Architecture

Professional-grade FastAPI backend with agents, tools, and multi-model LLM support.

---

## 🏗️ Architecture Overview

```
User Request
    ↓
FastAPI Gateway (6 REST endpoints)
    ↓
Orchestrator (intent routing)
    ↓
Specialized Agents (7 agents)
    ├─ DocumentAgent (ingest + OCR)
    ├─ RetrievalAgent (semantic search)
    ├─ QAAgent (question answering)
    ├─ ExplanationAgent (detailed explanations)
    ├─ ExecutionAgent (sandboxed code)
    ├─ PredictionAgent (exam question generation)
    └─ [Custom agents]
    ↓
MCP Tools (5 tools)
    ├─ VectorSearch (semantic)
    ├─ SQLQuery (structured data)
    ├─ PythonExec (sandboxed code)
    ├─ DocumentRetrieval (index/fetch)
    └─ StatsAnalysis (statistics)
    ↓
Services (business logic)
    ├─ SQLStoreService (SQLite)
    ├─ VectorStoreService (ChromaDB)
    ├─ OCRService (document parsing)
    └─ SandboxService (code execution)
    ↓
Storage Layer
    ├─ SQLite Database (relational data)
    ├─ ChromaDB (vector embeddings)
    └─ File System (uploads, temporary files)
```

---

## 📁 Project Structure

```
backend/
├── main.py                    ← FastAPI application entry point
├── requirements.txt           ← Python dependencies
├── Dockerfile                 ← Container image definition
├── README.md                  ← This file
│
├── agents/                    ← Agent implementations (intent handlers)
│   ├── __init__.py
│   ├── base_agent.py          ← BaseAgent abstract class
│   ├── document_agent.py      ← PDF ingestion & OCR
│   ├── retrieval_agent.py     ← Semantic search
│   ├── qa_agent.py            ← Question answering
│   ├── explanation_agent.py   ← Detailed explanations with citations
│   ├── execution_agent.py     ← Sandboxed Python code execution
│   ├── prediction_agent.py    ← Exam question generation
│   └── orchestrator.py        ← Multi-agent orchestration
│
├── tools/                     ← MCP Tools (Model Context Protocol)
│   ├── __init__.py
│   ├── base_tool.py           ← BaseTool abstract class
│   ├── vector_search.py       ← Semantic search tool
│   ├── sql_query.py           ← SQL query tool (DROP protected)
│   ├── python_exec.py         ← Python execution tool
│   ├── document_retrieval.py  ← Document index/fetch
│   ├── stats_analysis.py      ← Statistical analysis
│   └── registry.py            ← Tool registry & builder
│
├── services/                  ← Business logic layer
│   ├── __init__.py
│   ├── sql_store.py           ← SQL database operations
│   ├── vector_store.py        ← Vector store (ChromaDB)
│   ├── ocr_service.py         ← Document parsing & OCR
│   └── sandbox_service.py     ← Code execution sandbox
│
├── adapters/                  ← LLM provider adapters
│   ├── __init__.py
│   ├── base_adapter.py        ← ModelAdapter base class
│   ├── ollama_adapter.py      ← Ollama integration
│   ├── openai_adapter.py      ← OpenAI integration (stub)
│   ├── anthropic_adapter.py   ← Anthropic integration (stub)
│   └── vllm_adapter.py        ← vLLM integration (stub)
│
├── db/                        ← Database layer
│   ├── __init__.py
│   ├── models.py              ← SQLAlchemy ORM models
│   ├── session.py             ← Async session & utilities
│   └── migrations.sql         ← Database schema
│
├── gateway/                   ← REST API routes
│   ├── __init__.py
│   ├── router.py              ← API endpoints (6 routes)
│   └── schemas.py             ← Pydantic request/response models
│
├── config/                    ← Configuration
│   ├── __init__.py
│   ├── settings.py            ← Application settings
│   └── logging_config.py      ← Logging configuration
│
└── data/                      ← Runtime data (created on first run)
    ├── teleios.db             ← SQLite database file
    ├── uploads/               ← User uploaded files
    └── chroma/                ← ChromaDB vector data
```

---

## 🚀 Quick Start

### Install & Run

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8005
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8005
INFO:     Application startup complete
[info] db.ready url=sqlite+aiosqlite:///./data/teleios.db
[info] ollama_adapter.ready
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8005/health

# Ingest document
curl -X POST http://localhost:8005/ingest -F "file=@document.pdf"

# Get explanation
curl -X POST http://localhost:8005/explain \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this?", "doc_id": "doc_1"}'

# Generate questions
curl -X POST http://localhost:8005/predict \
  -H "Content-Type: application/json" \
  -d '{"doc_ids": ["doc_1"], "difficulty": "medium"}'

# Execute code
curl -X POST http://localhost:8005/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello\")"}'
```

---

## 📋 API Endpoints

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-03-19T12:00:00Z"
}
```

### POST `/ingest`
Upload and ingest a PDF document.

**Request:**
```
Content-Type: multipart/form-data
file: <PDF file>
```

**Response:**
```json
{
  "doc_id": "doc_abc123",
  "filename": "document.pdf",
  "pages": 42,
  "blocks": 156,
  "timestamp": "2026-03-19T12:00:00Z"
}
```

### POST `/explain`
Generate explanation for highlighted text.

**Request:**
```json
{
  "query": "What does this mean?",
  "doc_id": "doc_abc123",
  "highlighted_text": "Some relevant text from document"
}
```

**Response:**
```json
{
  "explanation": "Detailed explanation...",
  "answer": "Direct answer...",
  "citations": [
    {
      "source": "Page 5",
      "excerpt": "Relevant quote..."
    }
  ]
}
```

### POST `/predict`
Generate exam questions from documents.

**Request:**
```json
{
  "doc_ids": ["doc_abc123"],
  "difficulty": "medium"
}
```

**Response:**
```json
{
  "questions": [
    {
      "question": "What is...?",
      "difficulty": "medium",
      "options": ["A", "B", "C", "D"],
      "answer": "B",
      "explanation": "The correct answer is..."
    }
  ]
}
```

### POST `/execute`
Execute Python code in sandboxed environment.

**Request:**
```json
{
  "code": "import numpy as np\nprint(np.mean([1,2,3]))",
  "context": null,
  "doc_id": null
}
```

**Response:**
```json
{
  "status": "ok",
  "output": "2.0",
  "error": null,
  "figures": []
}
```

### POST `/analyze`
Analyze document and generate statistics.

**Request:**
```json
{
  "doc_ids": ["doc_abc123"],
  "group_by": "topic"
}
```

**Response:**
```json
{
  "groups": {
    "topic_1": {
      "question_count": 5,
      "avg_difficulty": 2.5
    }
  }
}
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Application
API_HOST=0.0.0.0
API_PORT=8005
API_RELOAD=true  # Enable auto-reload on code changes

# Database (SQLite)
DB_URL=sqlite+aiosqlite:///./data/teleios.db
DB_POOL_SIZE=5
DB_ECHO=false  # SQL query logging

# LLM Provider (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_TIMEOUT=60

# Vector Store (ChromaDB)
VECTOR_STORE_TYPE=chromadb
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_COLLECTION=teleios

# Logging
LOG_LEVEL=info
LOG_FILE=app.log
```

### Tool Configuration

Edit `config/tools.json` to enable/disable tools:

```json
{
  "tools": [
    {"name": "vector_search", "enabled": true},
    {"name": "sql_query", "enabled": true},
    {"name": "python_exec", "enabled": true},
    {"name": "document_retrieval", "enabled": true},
    {"name": "stats_analysis", "enabled": true}
  ]
}
```

---

## 🧠 Agent System

### BaseAgent Architecture

All agents inherit from `BaseAgent` and implement:

```python
class MyAgent(BaseAgent):
    name = "my_agent"
    description = "What this agent does"
    
    async def run(self, task: dict) -> dict:
        """Execute the agent task."""
        # Task contains intent-specific data
        # Returns dict with results
        pass
```

### Available Agents

| Agent | Purpose | Inputs | Outputs |
|-------|---------|--------|---------|
| **DocumentAgent** | Ingest PDFs | file, doc_id | blocks, pages |
| **RetrievalAgent** | Search documents | query, doc_id | results, scores |
| **QAAgent** | Answer questions | query, doc_id | answer, sources |
| **ExplanationAgent** | Explain concepts | query, doc_id, text | explanation, citations |
| **ExecutionAgent** | Run Python code | code, context, doc_id | output, error, figures |
| **PredictionAgent** | Generate questions | doc_ids, difficulty | questions, analysis |

### Agent Communication

Agents communicate through:
1. **Orchestrator**: Routes intents to agents
2. **Tools**: Shared MCP tools for common operations
3. **Services**: Shared business logic layer

```python
# Inside an agent:
async def run(self, task: dict) -> dict:
    # Use tool
    results = await self.use_tool("vector_search", query=task["query"])
    
    # Call LLM via adapter
    response = await self.adapter.generate(prompt="...")
    
    # Return results
    return {"answer": response, "sources": results}
```

---

## 🔧 MCP Tools

### Tool Interface

```python
class BaseTool(ABC):
    """Base class for Model Context Protocol tools."""
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass
```

### Available Tools

1. **VectorSearch**: Semantic search across documents
2. **SQLQuery**: Structured data queries (with security)
3. **PythonExec**: Sandboxed Python code execution
4. **DocumentRetrieval**: Index and fetch document content
5. **StatsAnalysis**: Statistical calculations

### Tool Permissions

Each agent has a whitelist of allowed tools:

```python
class MyAgent(BaseAgent):
    allowed_tools = [
        "vector_search",
        "document_retrieval",
    ]
    
    async def run(self, task: dict) -> dict:
        # This is allowed
        await self.use_tool("vector_search", ...)
        
        # This would raise PermissionError
        await self.use_tool("sql_query", ...)
```

---

## 🗄️ Database Schema

### ORM Models (SQLAlchemy)

```python
# Document
- id: UUID primary key
- external_id: Optional filename
- chunks_count: Number of text chunks
- created_at: Timestamp

# Block (document content)
- id: UUID primary key
- document_id: FK to Document
- content_type: text | equation | figure | table
- content: Text or metadata
- page_number: Where in document

# Question (generated exam question)
- id: UUID primary key
- document_id: FK to Document
- question_text: The question
- difficulty: 1-5 scale
- options: [A, B, C, D]
- correct_answer: String
```

### Create Tables

```bash
# On first run, main.py creates all tables via:
python -c "from db import init_db; init_db()"

# Or manually:
sqlite3 data/teleios.db < db/migrations.sql
```

---

## 📊 Logging

Configure logging in `config/logging_config.py`:

```python
import logging
import structlog

# Structured logging with context
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
)

logger = structlog.get_logger()
logger.info("event_happened", key="value")
```

### Log Levels

| Level | Use Case |
|-------|----------|
| DEBUG | Detailed troubleshooting |
| INFO | Normal operations (default) |
| WARNING | Issues to investigate |
| ERROR | Recoverable failures |
| CRITICAL | System-level failures |

---

## 🔐 Security Features

### SQL Injection Protection
- All SQL queries use parameterized statements
- DROP/DELETE commands rejected at runtime

```python
# ✅ Safe
await sql_tool.execute(
    "SELECT * FROM blocks WHERE doc_id = ?",
    [doc_id]
)

# ❌ Rejected
await sql_tool.execute(
    "DROP TABLE documents"
)
```

### Code Execution Sandboxing
- RestrictedPython for code evaluation
- Resource limits (memory, CPU time)
- Limited imports (whitelisted modules)

```python
# ✅ Allowed
code = "import numpy as np; print(np.mean([1,2,3]))"

# ❌ Rejected
code = "import os; os.system('rm -rf /')"
```

### Authentication & Authorization
- API key validation (future)
- Role-based access control (future)
- Rate limiting (future)

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_agents.py

# With coverage
pytest --cov=. --cov-report=html
```

### Test Structure

```
tests/
├── test_agents.py        ← Agent unit tests
├── test_tools.py         ← Tool unit tests
├── test_services.py      ← Service integration tests
├── test_gateway.py       ← API endpoint tests
└── fixtures/
    └── sample.pdf        ← Test document
```

### Example Test

```python
@pytest.mark.asyncio
async def test_qa_agent():
    agent = QAAgent(adapter=mock_adapter)
    result = await agent.run({
        "query": "What is X?",
        "doc_id": "test_doc"
    })
    
    assert "answer" in result
    assert result["status"] == "ok"
```

---

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t teleios-backend .

# Run container
docker run -p 8005:8005 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  teleios-backend
```

### Docker Compose

```bash
docker-compose up -d backend
```

### Production Checklist

- [ ] Set `API_RELOAD=false`
- [ ] Configure proper logging
- [ ] Set up monitoring/alerting
- [ ] Configure CORS if needed
- [ ] Use production-grade ASGI server (Gunicorn + Uvicorn)
- [ ] Set resource limits
- [ ] Configure reverse proxy (Nginx)

---

## 📚 Dependencies

### Core
- **FastAPI** 0.135.1 — Web framework
- **Pydantic** 2.12.5 — Data validation
- **SQLAlchemy** 2.0+ — ORM
- **Uvicorn** 0.42.0 — ASGI server

### LLM & AI
- **Ollama** (external) — Local LLM
- **ChromaDB** 0.4+ — Vector store
- **PyMuPDF** — PDF parsing
- **EasyOCR** — Optical character recognition

### Utilities
- **structlog** 24.x — Structured logging
- **python-dotenv** — Environment variables
- **httpx** — Async HTTP client
- **aiosqlite** — Async SQLite driver

See `requirements.txt` for complete list.

---

## 🐛 Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
pip install -r requirements.txt
```

**Error:** `Port 8005 already in use`
```bash
# Find and kill process
netstat -ano | findstr :8005
taskkill /PID <PID> /F
```

### Ollama connection error

**Error:** `Connection refused: http://localhost:11434`
```bash
# Start Ollama
ollama serve

# In new terminal, pull model
ollama pull qwen2.5-coder:3b
```

### Database errors

**Error:** `sqlite3.OperationalError: no such table`
```bash
# Initialize database
python -c "from db import init_db; init_db()"
```

---

## 📖 Additional Resources

- [PLAN.md](../PLAN.md) — Full system architecture
- [BUILD_PROGRESS.md](../BUILD_PROGRESS.md) — Implementation status
- [SETUP_GUIDE.md](../SETUP_GUIDE.md) — Setup instructions
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

---

**Built with ❤️ using FastAPI + SQLAlchemy + Ollama**
