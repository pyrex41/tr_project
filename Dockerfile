# syntax = docker/dockerfile:1

# Build stage for Elm frontend
FROM node:23.11.0-slim AS frontend-build

WORKDIR /app

# Install system dependencies for Elm (CA certificates and curl)
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Elm compiler
RUN npm install -g elm@latest-0.19.1

# Copy frontend files
COPY package*.json ./
COPY elm.json ./
COPY index.html ./
COPY vite.config.js ./
COPY src/ ./src/

# Install dependencies
RUN npm ci --include=dev

# Pre-download Elm packages to avoid SSL issues during build
RUN elm make src/Main.elm --output=/dev/null || true

# Build frontend
RUN npm run build

# Python backend stage - use official uv image
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS backend

WORKDIR /app

# Install system dependencies for Python packages
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install with uv (use cache mount for speed)
# Use minimal production requirements (NO ML dependencies)
COPY requirements-prod.txt .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements-prod.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend from previous stage
COPY --from=frontend-build /app/dist ./static

# Note: md_data/ is NOT copied - database is uploaded to persistent volume separately
# This reduces image size and deployment time

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DATABASE_PATH=/data/orders.db
ENV HOST=0.0.0.0
ENV PORT=8000
# Add /app to Python path so imports work
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run FastAPI with uvicorn, serving static files
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
