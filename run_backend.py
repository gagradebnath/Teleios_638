"""
Startup script for backend server.
Run this from the project root: python run_backend.py
"""
import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Starting Teleios Backend Server")
    print("=" * 60)
    print(f"Backend path: {backend_path}")
    print(f"Server URL: http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        reload_dirs=[backend_path]
    )
