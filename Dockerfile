# Use Python 3.11 slim image for smaller size and security
FROM python:3.11-slim

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser

# Copy dependency files first for better Docker layer caching
COPY pyproject.toml README.md LICENSE ./

# Install the package and its dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY the_data_packet/ ./the_data_packet/

# Create output directory with proper permissions
RUN mkdir -p /app/output && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set the CLI as the entrypoint
ENTRYPOINT ["python", "-m", "the_data_packet.cli"]

# Default help command
CMD ["--help"]

# Health check to ensure the container is working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import the_data_packet; print('Health check OK')" || exit 1

# Labels for better maintainability (OpenContainers format)
LABEL org.opencontainers.image.title="The Data Packet"
LABEL org.opencontainers.image.description="Automated podcast generation from news articles using AI"
LABEL org.opencontainers.image.version="2.0.0"
LABEL org.opencontainers.image.authors="TheWinterShadow <elijah.j.winter@outlook.com>"
LABEL org.opencontainers.image.source="https://github.com/TheWinterShadow/the_data_packet"
LABEL org.opencontainers.image.documentation="https://github.com/TheWinterShadow/the_data_packet/blob/main/README.md"
LABEL org.opencontainers.image.licenses="MIT"