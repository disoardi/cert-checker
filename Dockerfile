# Multi-stage Dockerfile for cert-checker

# Stage 1: Build stage
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application code
COPY cert_checker ./cert_checker


# Stage 2: Runtime stage
FROM python:3.11-slim

# Install runtime dependencies (including Java for keytool)
RUN apt-get update && apt-get install -y \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY cert_checker ./cert_checker
COPY config.toml.example ./config.toml.example

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# Create directory for configurations and certificates
RUN mkdir -p /config /certs

# Verify installation
RUN python -c "import cert_checker; print('cert-checker installed successfully')"

# Set entrypoint
ENTRYPOINT ["python", "-m", "cert_checker"]

# Default command (show help)
CMD ["--help"]
