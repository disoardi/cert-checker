# Multi-stage Dockerfile for cert-checker

# Stage 1: Build stage with Poetry
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY cert_checker ./cert_checker

# Install dependencies (no dev dependencies)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi


# Stage 2: Runtime stage
FROM python:3.11-slim

# Install runtime dependencies (including Java for keytool)
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY cert_checker ./cert_checker
COPY config.toml.example ./config.toml.example

# Set Python path
ENV PYTHONPATH=/app

# Create directory for configurations and certificates
RUN mkdir -p /config /certs

# Set entrypoint
ENTRYPOINT ["python", "-m", "cert_checker"]

# Default command (show help)
CMD ["--help"]
