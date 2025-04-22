
# syntax=docker/dockerfile:1

# --- Builder stage ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Copy requirements and install to a temp location
COPY requirements.txt .
RUN pip install --user --upgrade pip && pip install --user -r requirements.txt

# --- Final stage ---
FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files
COPY main.py .
COPY --from=builder /root/.local /root/.local

# Set environment variables for security
ENV PATH=/root/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Use a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
