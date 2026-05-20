# =============================================================================
# Dockerfile — CyberdeckCSS360
# Multi-stage: builds the React frontend, then serves it via Flask
# =============================================================================

# ── Stage 1: Build React/Vite frontend ───────────────────────────────────────
FROM node:20-alpine AS frontend-build

WORKDIR /app

# Install dependencies first (better layer caching)
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build
COPY index.html vite.config.js ./
COPY src/ ./src/
RUN npm run build
# Output lands in /app/dist

# ── Stage 2: Python / Flask API ───────────────────────────────────────────────
FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY api/requirements.txt ./api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

# Copy API source
COPY api/ ./api/

# Copy built frontend from stage 1
COPY --from=frontend-build /app/dist ./dist

# Expose Flask port
EXPOSE 5000

# Environment defaults (overridden by .env / docker-compose)
ENV FLASK_APP=api.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1

# Start Flask
CMD ["python", "api/api.py"]
