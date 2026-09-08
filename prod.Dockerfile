# Stage 1: Build Astro static frontend
FROM node:22-bookworm-slim AS frontend-builder

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
# Configure client-side API requests to use relative /api/v1 (same-origin)
ENV PUBLIC_API_BASE_URL=/api/v1
RUN npm run build

# Stage 2: Production Python FastAPI container
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.28 /uv /usr/local/bin/uv

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    APP_FRONTEND_DIST_DIR="/app/frontend_dist"

# Install backend dependencies
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked --no-dev

# Copy application source code
COPY backend/app ./app

# Copy compiled static frontend from stage 1
COPY --from=frontend-builder /app/dist ./frontend_dist

EXPOSE 8000

# Run FastAPI with uvicorn (single process, ideal for ECS Fargate container)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
