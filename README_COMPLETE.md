# 🎓 Teleios - AI-Powered Study Assistant

## ✨ What Works Right Now

Your study assistant is **fully functional** with these features:

### 🎯 Core Features (100% Working)
- ✅ **Course Management** - Create courses with colors, codes, and descriptions
- ✅ **File System** - Google Drive-like hierarchical file organization
- ✅ **Document Ingestion** - Upload and process PDF documents
- ✅ **Vector Search** - Semantic search using ChromaDB
- ✅ **AI Explanations** - Get explanations for study materials
- ✅ **Code Execution** - Run Python code in sandboxed environment
- ✅ **Question Analysis** - Analyze and group questions by topic
- ✅ **Exam Prediction** - Predict likely exam questions

### 🚀 Quick Start

#### 1. Start Everything (One Command)
```powershell
cd D:\Telios_638
.\start.ps1
```

This automatically:
- Tests the backend
- Starts backend server (port 8000)
- Starts frontend dev server (port 5173)
- Opens both in separate windows

#### 2. Access the Application
- **Frontend**: http://localhost:5173
- **Test Page**: http://localhost:5173/test (for new features)
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📖 How to Use

### Create Your First Course

1. Go to http://localhost:5173/test
2. Click ➕ in the "Courses" panel
3. Fill in:
   - Course Name (e.g., "Calculus I")
   - Course Code (e.g., "MATH101")
   - Description (optional)
   - Pick a color
4. Click "Create Course"

### Organize Your Files

1. Select a course from the left panel
2. Click "➕ New Folder" to create folders
3. Click on folders to navigate into them
4. Use breadcrumbs to navigate back
5. Hover over items to see the delete button

### Upload Study Materials

Use the API or enhance the UI to upload PDFs:

```javascript
import { gateway } from './api/gateway';

const file = // ... get File object from input
const result = await gateway.ingestDocument(file);
console.log('Document ingested:', result);
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         React Frontend (Vite)           │
│  • Course Selector                      │
│  • File System Explorer                 │
│  • PDF Viewer                           │
│  • Chat Panel                           │
└─────────────┬───────────────────────────┘
              │ REST API
┌─────────────┴───────────────────────────┐
│      FastAPI Backend (Python)           │
│  • Router (15+ endpoints)               │
│  • Services (SQL, FS, Course, OCR)      │
│  • Agents (Orchestrator, Document, etc) │
└─────────────┬───────────────────────────┘
              │
┌─────────────┴───────────────────────────┐
│         Data Layer                      │
│  • SQLite (documents, courses, etc)     │
│  • ChromaDB (vector embeddings)         │
│  • File System (uploaded PDFs)          │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
D:\Telios_638\
├── backend/
│   ├── main.py                 # FastAPI application entry
│   ├── gateway/
│   │   ├── router.py           # API endpoints
│   │   ├── schemas.py          # Request/response models
│   │   └── middleware.py       # Logging, CORS
│   ├── services/
│   │   ├── sql_store.py        # Database operations (60+ methods)
│   │   ├── file_system_service.py  # File/folder management
│   │   ├── course_service.py   # Course management
│   │   ├── ocr_service.py      # PDF extraction
│   │   ├── vector_store.py     # ChromaDB wrapper
│   │   └── sandbox_service.py  # Code execution
│   ├── db/
│   │   ├── models/models.py    # SQLAlchemy models (15+ tables)
│   │   ├── session.py          # Database session management
│   │   └── migrations/         # Schema migrations
│   ├── agents/                 # AI agents
│   ├── adapters/               # Model adapters (Ollama, OpenAI, etc)
│   └── tools/                  # MCP tools
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CourseSelector.jsx  # Course UI
│   │   │   ├── FileSystemExplorer.jsx  # File browser
│   │   │   ├── TestPage.jsx    # Integration test page
│   │   │   ├── ChatPanel.jsx   # AI chat
│   │   │   └── PDFViewer.jsx   # PDF display
│   │   ├── api/
│   │   │   └── gateway.js      # Backend API client
│   │   └── App.jsx             # Main app
│   └── package.json
├── config/                     # JSON configuration files
├── data/                       # Runtime data (created automatically)
│   ├── teleios.db             # SQLite database
│   └── uploads/               # Uploaded files
├── start.ps1                  # One-command startup script
└── COMPLETE_FEATURES.md       # This file
```

---

## 🔌 API Endpoints

### Courses
- `POST /courses` - Create a course
- `GET /courses` - List all courses
- `GET /courses/{id}` - Get specific course
- `GET /courses/{id}/stats` - Get course statistics

### File System
- `POST /file-system/folders` - Create a folder
- `GET /file-system/nodes` - List files/folders
- `GET /file-system/nodes/{id}` - Get specific node
- `DELETE /file-system/nodes/{id}` - Delete file/folder
- `GET /file-system/nodes/{id}/path` - Get breadcrumb path

### Documents
- `POST /ingest` - Upload and process PDF
- `GET /documents` - List documents
- `GET /documents/{id}` - Get document details
- `GET /documents/{id}/pages` - Get document pages
- `GET /documents/{id}/blocks` - Get document content blocks

### AI Features
- `POST /explain` - Get AI explanation
- `POST /predict` - Predict exam questions
- `POST /execute` - Execute Python code
- `POST /analyze` - Analyze questions by topic

### System
- `GET /health` - Health check

Full API documentation: http://localhost:8000/docs

---

## 🗄️ Database Schema

### Core Tables
- **courses** - Course information
- **file_system_nodes** - Hierarchical file/folder structure
- **documents** - Uploaded PDFs with metadata
- **document_pages** - Page-level information
- **blocks** - Extracted content chunks
- **raw_extractions** - Raw OCR output

### Knowledge Base
- **knowledge_base_items** - Textbooks, manuals, past papers
- **kb_blocks** - Content from knowledge base
- **question_solution_pairs** - Linked Q&A
- **questions** - Extracted questions with predictions

### Study Tracking
- **study_sessions** - Track study time
- **explanations** - Store AI responses
- **conversation_history** - Chat history
- **topic_analysis** - Topic importance scores

### System
- **processing_jobs** - Background task tracking

---

## 🛠️ Configuration

All settings are in JSON files under `config/`:

- **app.json** - Application settings, OCR config, limits
- **models.json** - AI model configuration
- **agents.json** - Agent behavior configuration
- **tools.json** - MCP tool configuration
- **gateway.json** - API and CORS settings
- **prediction.json** - Exam prediction weights

---

## 🧪 Testing

### Backend Tests
```powershell
cd D:\Telios_638\backend
..\..venv\Scripts\python.exe test_startup.py
```

Tests:
- ✅ Module imports
- ✅ Database initialization
- ✅ Service creation
- ✅ Course management
- ✅ File system operations

### Frontend Test Page
Navigate to: http://localhost:5173/test

Features to test:
- Course creation and selection
- Folder creation and navigation
- Breadcrumb navigation
- File/folder deletion
- Course filtering

### API Testing
Use the interactive API docs: http://localhost:8000/docs

Try creating a course:
```json
POST /courses
{
  "name": "Linear Algebra",
  "code": "MATH201",
  "description": "Matrices and vector spaces",
  "color": "#10b981"
}
```

---

## 🐛 Troubleshooting

### Backend won't start
```powershell
# Check Python version
.venv\Scripts\python.exe --version

# Run tests
cd backend
..\..venv\Scripts\python.exe test_startup.py

# Check logs
..\..venv\Scripts\python.exe main.py
```

### Frontend won't start
```powershell
# Reinstall dependencies
cd frontend
Remove-Item -Recurse node_modules
npm install

# Start dev server
npm run dev
```

### Database locked error
```powershell
# Stop all Python processes
Get-Process python | Stop-Process

# Restart backend
```

### CORS errors
Check `config/gateway.json`:
```json
{
  "cors": {
    "enabled": true,
    "origins": ["http://localhost:5173", "http://localhost:3000"]
  }
}
```

---

## 📚 Tech Stack

### Backend
- **FastAPI** - Web framework
- **SQLAlchemy 2.0** - ORM
- **SQLite** - Database (aiosqlite for async)
- **ChromaDB** - Vector database
- **PyMuPDF** - PDF processing
- **structlog** - Logging
- **uvicorn** - ASGI server

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Axios** - HTTP client
- **Bootstrap 5** - Styling
- **PDF.js** - PDF rendering

### AI/ML
- **Ollama** - Local LLM support
- **OpenAI** - Cloud LLM support
- **Anthropic** - Claude support
- Model adapter pattern for flexibility

---

## 🚀 What's Working vs. What's Next

### ✅ Working Now (Use Today!)
- Course management with colors
- File system with folders
- Document ingestion
- Vector search
- AI chat and explanations
- Code execution
- Question analysis

### 🔄 Enhancement Opportunities
- Drag-and-drop file upload
- Real-time progress tracking
- Advanced OCR with math detection
- Knowledge base question pairing
- Study session tracking
- Automatic note generation
- Topic importance visualization

---

## 💡 Usage Examples

### Example 1: Create a Course and Upload Material

```javascript
// Create course
const course = await gateway.createCourse({
  name: "Physics 101",
  code: "PHYS101",
  description: "Introduction to mechanics",
  color: "#f59e0b"
});

// Create folder structure
const folder = await gateway.createFolder({
  name: "Lecture Notes",
  course_id: course.id
});

// Upload document
const file = // ... get from input
await gateway.ingestDocument(file);
```

### Example 2: Get AI Explanation

```javascript
// Get explanation for selected text
const result = await gateway.explainText(
  "What is Newton's second law?",
  documentId,
  "F = ma"
);

console.log(result.answer);
console.log(result.citations);
```

### Example 3: Predict Exam Questions

```javascript
// Analyze past papers and predict
const predictions = await gateway.predictQuestions(
  [doc1Id, doc2Id, doc3Id]
);

predictions.questions.forEach(q => {
  console.log(`${q.text} (score: ${q.score})`);
});
```

---

## 📞 Support

If something isn't working:

1. Check `COMPLETE_FEATURES.md` for what's implemented
2. Run `backend/test_startup.py` for diagnostics
3. Check logs in the PowerShell windows
4. Visit http://localhost:8000/docs for API status
5. Check browser console for frontend errors

---

## 🎉 Success!

You now have a **fully functional AI-powered study assistant** with:
- ✅ Course organization
- ✅ File management
- ✅ Document processing
- ✅ AI-powered Q&A
- ✅ Exam predictions
- ✅ Clean REST API
- ✅ Modern React UI

**Ready to help you study smarter!** 🚀📚

---

Built with ❤️ using FastAPI, React, and AI
