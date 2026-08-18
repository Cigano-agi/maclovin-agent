# Production Dockerfile for Maclovin News Autonomous Pipeline
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SUPABASE_URL=https://rvoyllttmlluhwenhyln.supabase.co \
    SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ2b3lsbHR0bWxsdWh3ZW5oeWxuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU3OTY0MjAsImV4cCI6MjA5MTM3MjQyMH0.wLXV1lUTIT1VTzvS_tq_X6k3K2uClK_0qjvOKjGEv9Y

# Install build dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache

COPY . .

# Run daily ingestion pipeline by default, or background scheduler
CMD ["uv", "run", "python", "-m", "maclovin", "run"]
