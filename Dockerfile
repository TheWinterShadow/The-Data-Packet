# Multi-stage build for smaller, more secure image
# ==============================================================================
# Image metadata and labels
# ==============================================================================

# Stage 1: Build stage
# ==============================================================================
FROM python:3.11-slim AS builder

# Add metadata labels
LABEL maintainer="TheWinterShadow <elijah.j.winter@outlook.com>"
LABEL org.opencontainers.image.title="The Data Packet"
LABEL org.opencontainers.image.description="Automated podcast generation from news articles using AI"
LABEL org.opencontainers.image.version="2.0.0"
LABEL org.opencontainers.image.authors="TheWinterShadow <elijah.j.winter@outlook.com>"
LABEL org.opencontainers.image.url="https://github.com/TheWinterShadow/The-Data-Packet"
LABEL org.opencontainers.image.source="https://github.com/TheWinterShadow/The-Data-Packet"
LABEL org.opencontainers.image.documentation="https://github.com/TheWinterShadow/The-Data-Packet/blob/main/README.md"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.vendor="TheWinterShadow"

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /build

# Copy dependency files first for better Docker layer caching
COPY pyproject.toml README.md LICENSE ./

# Copy source code for version detection
COPY the_data_packet/ ./the_data_packet/

# Install the package and its dependencies
RUN pip install --no-cache-dir -e .

# ==============================================================================
# Stage 2: Runtime stage
# ==============================================================================
FROM python:3.11-slim AS runtime

# Add runtime metadata labels
LABEL maintainer="TheWinterShadow <elijah.j.winter@outlook.com>"
LABEL org.opencontainers.image.title="The Data Packet"
LABEL org.opencontainers.image.description="Automated podcast generation from news articles using AI"
LABEL org.opencontainers.image.version="2.0.0"
LABEL org.opencontainers.image.authors="TheWinterShadow <elijah.j.winter@outlook.com>"
LABEL org.opencontainers.image.url="https://github.com/TheWinterShadow/The-Data-Packet"
LABEL org.opencontainers.image.source="https://github.com/TheWinterShadow/The-Data-Packet"
LABEL org.opencontainers.image.documentation="https://github.com/TheWinterShadow/The-Data-Packet/blob/main/README.md"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.vendor="TheWinterShadow"

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Install only runtime dependencies (minimal)
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --create-home --shell /bin/bash --uid 1000 --gid 1000 appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY the_data_packet/ ./the_data_packet/
COPY pyproject.toml README.md LICENSE ./

# Create output directory with proper permissions
RUN mkdir -p /app/output && \
    chown -R appuser:appgroup /app && \
    chmod 755 /app/output

# Switch to non-root user
USER appuser

# Expose healthcheck port (optional for monitoring)
EXPOSE 8080

# Set the CLI as the entrypoint
ENTRYPOINT ["python", "-m", "the_data_packet.cli"]

# Default help command
CMD ["--help"]

# Health check to ensure the container is working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import the_data_packet; print('Health check OK')" || exit 1

# Labels for better maintainability (OpenContainers format)
LABEL org.opencontainers.image.title="The Data Packet" \
      org.opencontainers.image.description="AI-powered automated podcast generation from tech news articles" \
      org.opencontainers.image.version="2.0.0" \
      org.opencontainers.image.authors="TheWinterShadow <elijah.j.winter@outlook.com>" \
      org.opencontainers.image.url="https://github.com/TheWinterShadow/The-Data-Packet" \
      org.opencontainers.image.documentation="https://thewintershadow.github.io/the_data_packet/" \
      org.opencontainers.image.source="https://github.com/TheWinterShadow/The-Data-Packet" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.vendor="TheWinterShadow"
LABEL org.opencontainers.image.version="2.0.0"
LABEL org.opencontainers.image.authors="TheWinterShadow <elijah.j.winter@outlook.com>"
LABEL org.opencontainers.image.source="https://github.com/TheWinterShadow/the_data_packet"
LABEL org.opencontainers.image.documentation="https://github.com/TheWinterShadow/the_data_packet/blob/main/README.md"
LABEL org.opencontainers.image.licenses="MIT"