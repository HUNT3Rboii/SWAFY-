# Vision worker service.
# Runs as a non-root user. Only needs to start, read config, print a log line
# and stay alive (no backend polling yet - that depends on BE-4).
FROM python:3.11-slim

WORKDIR /app

# Runtime deps only (requirements.txt is pinned).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source.
COPY src/ ./src/
COPY schema.json .

# Create a non-root user and switch to it.
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Add /app/src to Python path so python -m vision_worker finds the package
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    LOG_LEVEL=info

EXPOSE 8000

CMD ["python", "-m", "vision_worker"]