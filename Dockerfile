# =============================================================================
# Builder Stage
# =============================================================================
FROM python:3.10-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install only what is needed for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better cache)
COPY requirements.txt .

# Install dependencies into /install
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefer-binary --prefix=/install -r requirements.txt


# =============================================================================
# Runtime Stage
# =============================================================================
FROM python:3.10-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH"

WORKDIR /app

# Create non-root user
RUN useradd -m appuser

# Copy only installed dependencies
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Fix permissions
RUN chown -R appuser:appuser /app

# Remove build tools (IMPORTANT size reduction)
RUN apt-get update && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

USER appuser

EXPOSE 8000

# Production command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]