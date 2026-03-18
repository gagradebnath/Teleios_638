FROM python:3.12-slim

WORKDIR /app

# Install system dependencies needed by various packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure data directories exist for SQLite and uploads
RUN mkdir -p /app/data/uploads /app/logs

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8005/health || exit 1

EXPOSE 8005

# Start FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]