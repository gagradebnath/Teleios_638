# Teleios Startup and Test Script
# This script starts the backend and runs comprehensive tests

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TELEIOS - STARTUP AND TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set error action preference
$ErrorActionPreference = "Continue"

# Check if virtual environment exists
if (-Not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create it first: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Virtual environment found" -ForegroundColor Green

# Step 1: Run backend tests
Write-Host ""
Write-Host "Step 1: Running backend tests..." -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray

cd backend
$testOutput = & ..\..venv\Scripts\python.exe test_startup.py
$testExitCode = $LASTEXITCODE
Write-Host $testOutput

if ($testExitCode -eq 0) {
    Write-Host "✅ Backend tests passed" -ForegroundColor Green
} else {
    Write-Host "❌ Backend tests failed" -ForegroundColor Red
    Write-Host "Please fix the errors before continuing" -ForegroundColor Yellow
    cd ..
    exit 1
}

cd ..

# Step 2: Check frontend dependencies
Write-Host ""
Write-Host "Step 2: Checking frontend..." -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray

cd frontend

if (-Not (Test-Path "node_modules")) {
    Write-Host "⚠️  node_modules not found" -ForegroundColor Yellow
    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ npm install failed" -ForegroundColor Red
        cd ..
        exit 1
    }
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ Frontend dependencies found" -ForegroundColor Green
}

cd ..

# Step 3: Start backend server
Write-Host ""
Write-Host "Step 3: Starting backend server..." -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API docs will be at: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; ..\..venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Step 4: Start frontend dev server
Write-Host ""
Write-Host "Step 4: Starting frontend dev server..." -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "Frontend will be available at: http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start frontend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TELEIOS IS STARTING!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "To test new features, navigate to:" -ForegroundColor Yellow
Write-Host "  http://localhost:5173/test" -ForegroundColor Cyan
Write-Host ""
Write-Host "Close the PowerShell windows to stop the servers" -ForegroundColor Gray
Write-Host ""
