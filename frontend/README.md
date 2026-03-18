# Teleios Frontend

React-based UI for the Teleios study assistant platform.

## Quick Start

### Prerequisites
- Node.js 18+ and npm 9+
- Backend API running on localhost:8005

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Frontend runs on `http://localhost:5173`

### Build

```bash
npm run build
```

Optimized build output in `dist/`

### Lint

```bash
npm run lint
```

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML entry point
├── src/
│   ├── api/
│   │   └── gateway.js      # Backend API client
│   ├── components/
│   │   ├── ChatPanel.jsx   # Explanation & QA interface
│   │   ├── IngestPanel.jsx # Document upload
│   │   ├── PredictionPanel.jsx # Question generation
│   │   ├── ExecutionPanel.jsx  # Code execution
│   │   ├── PDFViewer.jsx   # PDF rendering with pdf.js
│   │   ├── LeftPanel.jsx   # Document display container
│   │   ├── RightPanel.jsx  # Panel router
│   │   ├── StudyLayout.jsx # 50/50 grid layout
│   │   └── TabBar.jsx      # Tab navigation
│   ├── App.jsx             # Main app with state management
│   ├── main.jsx            # React entry point
│   ├── index.css           # Global styles
│   ├── App.css             # App container styles
│   └── components/
│       └── *.css           # Component-specific styles
├── vite.config.js          # Vite configuration
├── package.json            # Dependencies & scripts
└── .eslintrc.json          # ESLint rules
```

## Architecture

### State Management
- **App.jsx**: Central state management with hooks
- **Props Drilling**: Direct prop passing to components
- Global state: activePdf, chatHistory, documentId, questions, executionOutput

### Component Hierarchy
```
App
├── StudyLayout (50/50 grid)
│   ├── LeftPanel
│   │   └── PDFViewer
│   ├── Divider
│   └── RightPanel
│       ├── TabBar
│       └── [Active Panel]
│           ├── ChatPanel
│           ├── IngestPanel
│           ├── PredictionPanel
│           └── ExecutionPanel
```

### API Integration
- **gateway.js**: Axios-based client with interceptors
- **Endpoints**: /ingest, /explain, /predict, /execute, /analyze
- **Error Handling**: Try-catch + user feedback

### PDF Viewer
- **pdfjs-dist**: Mozilla PDF.js library
- **Features**: Page navigation, zoom, text selection
- **Text Selection**: Sends highlighted text to backend for explanation

## Features

### 1. Chat Panel (💬)
- Ask questions about documents
- Get LLM-powered explanations with citations
- Highlight text to request explanations
- Chat history visualization

### 2. Ingest Panel (📤)
- Drag-and-drop PDF upload
- File validation (PDF only)
- Document API integration
- Success feedback

### 3. Prediction Panel (❓)
- Generate exam questions (easy/medium/hard)
- Document analysis by topic/difficulty
- Question statistics
- Export-ready format

### 4. Execution Panel (⚙️)
- Python code editor with syntax highlighting
- Template library (stats, plots, analysis)
- Sandboxed code execution
- Output display with error handling

## Dependencies

### Production
- **react**: UI framework
- **react-dom**: React rendering
- **pdfjs-dist**: PDF viewer
- **axios**: HTTP client
- **zustand**: State management (optional future use)

### Development
- **vite**: Fast build tool
- **@vitejs/plugin-react**: React plugin
- **eslint**: Code linting
- **eslint-plugin-react**: React-specific rules

## Configuration

### Environment Variables
Create `.env` file (copy from `.env.example`):

```
VITE_API_URL=http://localhost:8005
VITE_APP_NAME=Teleios Study Assistant
VITE_PDF_MAX_SIZE=52428800
VITE_ENABLE_DEBUG=true
```

### Vite Configuration
- Port: 5173
- Proxy: `/api` → backend
- Build: Optimized chunks (pdf-js, api)
- Source maps enabled

## Development Tips

### Debugging
- Check browser console for API errors
- Verify backend running on 8005
- Use React DevTools extension
- Check network tab for API calls

### Component Development
- Each panel is independent
- Props are typed in function signatures
- CSS modules scoped per component
- Use semantic HTML for accessibility

### Testing
- Test PDF upload or ingest first
- Use browser DevTools for network inspection
- Test on both desktop and mobile views
- Verify API responses match schemas

## Future Enhancements

- [ ] Local state management with Zustand
- [ ] WebSocket for real-time updates
- [ ] Dark mode toggle
- [ ] Keyboard shortcuts
- [ ] Export chat as PDF
- [ ] Multi-document comparison
- [ ] User authentication
- [ ] Document annotations
- [ ] Collaborative study sessions

## Troubleshooting

### API Connection Failed
- Ensure backend is running: `uvicorn main:app --reload --host 0.0.0.0 --port 8005`
- Check VITE_API_URL environment variable
- Verify CORS headers from backend

### PDF Not Displaying
- Check file is valid PDF
- Verify file size < 50MB
- Check browser console for pdf.js errors

### Code Execution Timeout
- Code may be too complex
- Check backend logs for errors
- 30-second timeout limit

## License

See root LICENSE file.
