# =====================================================================
# Stage 1: Build the React Frontend
# =====================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY incident-investigation-agent/frontend/package*.json ./
RUN npm install

COPY incident-investigation-agent/frontend/ ./
RUN npm run build

# =====================================================================
# Stage 2: Python Backend with Unified Static Serving
# =====================================================================
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY incident-investigation-agent/backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source
COPY incident-investigation-agent/backend/ ./backend/

# Copy built frontend assets from stage 1 into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 8000

WORKDIR /app/backend
CMD ["python", "main.py"]
