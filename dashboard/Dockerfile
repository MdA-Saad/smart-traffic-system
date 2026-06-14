FROM python:3.9-slim

# Prevent memory buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Pull the ultra-fast 'uv' package manager directly into the container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd -m appuser
WORKDIR /app

# Use 'uv pip' to install your exact stack instantly and cleanly
RUN uv pip install --system --no-cache fastapi uvicorn sqlalchemy apscheduler

COPY --chown=appuser:appuser dashboard.py .

USER appuser

# Execute the module (dashboard:app) and lock it to 1 worker for your 1-core VM
CMD ["uvicorn", "dashboard:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
