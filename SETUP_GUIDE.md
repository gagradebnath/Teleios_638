# Teleios Study Assistant — Quick Start Guide

Complete end-to-end setup for local development. **Est. time: 15 minutes**

---

## 📋 Prerequisites

- **Python 3.11+** with pip/venv
- **Node.js 18+** with npm
- **Ollama** running locally (or adjust backend config for alternative LLM)
- **Git** (optional, for version control)

---

## 🚀 One-Command Setup (Windows PowerShell)

```powershell
# From project root (d:\Teleios_638\)
.\init.cmd
```

This script will:
1. ✅ Create Python virtual environment
2. ✅ Install backend dependencies
3. ✅ Initialize SQLite database
4. ✅ Install frontend dependencies
5. ✅ Display startup commands

**If init.cmd doesn't exist, follow manual setup below.**

---

## 🔧 Manual Setup

### Step 1: Backend Setup (Python/FastAPI)

```bash
# From project root
cd backend

# Create virtual environment
python -m venv .venv

# Activate environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed ✓')"
```

### Step 2: Configure Backend Environment

```bash
# Copy example environment
cp ..\.env.example ..\.env

# Edit .env if needed (defaults work for local Ollama)
# Key settings:
# - OLLAMA_BASE_URL=http://localhost:11434
# - DB_URL=sqlite+aiosqlite:///./data/teleios.db
# - LOG_LEVEL=info
```

### Step 3: Start Backend

```bash
# From project root (with venv activated)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8005
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8005
INFO:     Application startup complete
2026-03-19 12:00:00 [info] db.ready url=sqlite+aiosqlite:///./data/teleios.db
2026-03-19 12:00:01 [info] ollama_adapter.ready
```

### Step 4: Frontend Setup (React/Vite)

**In a new terminal window:**

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Copy example environment (optional)
cp .env.example .env
```

### Step 5: Start Frontend

```bash
# From frontend/ directory
npm run dev
```

**Expected output:**
```
  ➜  Local:   http://localhost:5173/
  ➜  Press h to show help
```

---

## ✅ Verify Setup

### Check Backend Health

```bash
# From new terminal, test API
curl http://localhost:8005/health

# Expected response:
# {"status":"ok","timestamp":"2026-03-19T12:00:00Z"}
```

### Check Frontend Build

Navigate to `http://localhost:5173/` in browser. You should see:
- 📄 Document panel (left, empty)
- 💬 Chat panel (right, with welcome message)
- Tab bar with Chat, Ingest, Predict, Execute tabs

---

## 🧪 First Test: Upload & Chat

### 1. Upload a Document
- Click **Ingest** tab
- Drag-drop or browse for a PDF file
- Wait for upload (shows "⏳ Uploading...")

### 2. Ask a Question
- Click **Chat** tab
- Type: "What is this document about?"
- Click "📤 Send"

### 3. View Response
- Assistant reply appears with citations
- Try highlighting text in PDF for instant explanations

---

## 🐙 Optional: Run with Docker Compose (Experimental)

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Watch logs
docker-compose logs -f

# Stop all services
docker-compose down
```

**Services:**
- **teleios-backend**: FastAPI on port 8005
- **teleios-frontend**: React dev server on port 5173
- **ollama**: LLM (if enabled in docker-compose.yml)

---

## 📁 Project Structure

```
Teleios_638/
├── backend/
│   ├── .venv/                 ← Python virtual environment
│   ├── main.py                ← FastAPI app entry point
│   ├── agents/                ← Agent implementations (7 agents)
│   ├── tools/                 ← MCP tools (5 tools)
│   ├── services/              ← Business logic layer
│   ├── db/                    ← Database models & ORM
│   ├── gateway/               ← API routes (6 endpoints)
│   ├── requirements.txt        ← Python dependencies
│   └── config/
│       ├── tools.json         ← MCP tool definitions
│       └── agents.json        ← Agent configuration
│
├── frontend/
│   ├── node_modules/          ← NPM packages (after npm install)
│   ├── src/
│   │   ├── App.jsx            ← Main React component
│   │   ├── components/        ← UI components (8 components)
│   │   ├── api/
│   │   │   └── gateway.js     ← Backend API client
│   │   ├── index.css          ← Global styles
│   │   └── main.jsx           ← React entry point
│   ├── public/
│   │   └── index.html         ← HTML template
│   ├── package.json           ← NPM dependencies
│   ├── vite.config.js         ← Vite build config
│   └── .eslintrc.json         ← Linting rules
│
├── config/
│   ├── tools.json             ← MCP tool registry
│   └── agents.json            ← Agent registry
│
├── data/
│   └── teleios.db             ← SQLite database (created on first run)
│
├── docker-compose.yml         ← Container orchestration
├── .env.example               ← Environment variables template
├── BUILD_PROGRESS.md          ← This file (progress tracker)
├── SETUP_GUIDE.md             ← Setup instructions (this file)
└── README.md                  ← Project overview
```

---

## 🔌 Environment Variables

### Backend (.env)

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Database
DB_URL=sqlite+aiosqlite:///./data/teleios.db
DB_POOL_SIZE=5

# Vector Store
VECTOR_STORE_TYPE=memory  # or: chromadb
CHROMADB_URL=http://localhost:8000

# API
API_HOST=0.0.0.0
API_PORT=8005
API_RELOAD=true

# Logging
LOG_LEVEL=info
```

### Frontend (.env)

```bash
# API Configuration
VITE_API_URL=http://localhost:8005

# Feature Flags
VITE_ENABLE_DEBUG=true
VITE_ENABLE_ANALYTICS=false

# PDF Viewer
VITE_PDF_MAX_SIZE=52428800  # 50MB in bytes
```

---

## 🐛 Troubleshooting

### Backend Won't Start

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`  
**Solution:** Activate virtual environment and run `pip install -r requirements.txt`

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

**Problem:** `Address already in use: ('0.0.0.0', 8005)`  
**Solution:** Another process is using port 8005. Kill it or use different port:

```bash
# Kill process on port 8005
netstat -ano | findstr :8005
taskkill /PID <PID> /F

# Or start on different port
uvicorn main:app --port 8006
```

### Frontend Won't Build

**Problem:** `npm: command not found`  
**Solution:** Install Node.js from https://nodejs.org/

**Problem:** `Cannot find module 'react'`  
**Solution:** Run `npm install` in frontend directory

```bash
cd frontend
npm install
npm run dev
```

### API Connection Failed

**Problem:** Frontend can't reach backend  
**Solution:** 
1. Verify backend is running: `curl http://localhost:8005/health`
2. Check VITE_API_URL in frontend/.env matches backend URL
3. Check browser console for CORS errors

**Problem:** PDF upload fails  
**Solution:**
1. Check file is valid PDF (not corrupted)
2. Check file size < 50MB
3. Check backend logs for `OCRService` errors

### Ollama Connection Error

**Problem:** `Connection refused: http://localhost:11434`  
**Solution:**
1. Start Ollama: `ollama serve`
2. In new terminal, pull model: `ollama pull qwen2.5-coder:3b`
3. Verify it's running: `curl http://localhost:11434/api/tags`

---

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Storage | 2 GB | 10 GB (for PDFs + models) |
| OS | Windows 10, macOS 11, Ubuntu 20.04 | Latest stable |
| Python | 3.11 | 3.12 |
| Node.js | 18 | 20+ |

---

## 🚀 Production Deployment

### Option 1: Docker Compose (Recommended for local)

```bash
docker-compose up -d
```

### Option 2: Kubernetes (Advanced)

```bash
kubectl apply -f k8s/
```

### Option 3: Cloud (AWS/Azure/GCP)

Refer to [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) *(to be added)*

---

## 📚 Next Steps

1. **Upload your first PDF**: Use the Ingest tab to test document ingestion
2. **Ask questions**: Try the Chat tab to test the Q&A system
3. **Generate questions**: Use Predict tab to create exam questions
4. **Execute code**: Use Execute tab to run Python analysis scripts
5. **Read docs**: See [frontend/README.md](frontend/README.md) and [backend/README.md](backend/README.md)

---

## 🤝 Support

- **Logs**: Check `backend/app.log` and browser console
- **Issues**: Create GitHub issue with reproduction steps
- **Documentation**: See [BUILD_PROGRESS.md](BUILD_PROGRESS.md) for architecture details

---

**Happy studying! 📚**
