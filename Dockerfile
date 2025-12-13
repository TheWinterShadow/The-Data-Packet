# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml first for better Docker layer caching
COPY pyproject.toml .

# Install the package and its dependencies
COPY . .
RUN pip install --no-cache-dir .

# Create output directory
RUN mkdir -p /app/output

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Default command - can be overridden
CMD ["python", "scraper_main.py"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import the_data_packet; print('Package loaded successfully')" || exit 1

# Labels for metadata
LABEL maintainer="TheWinterShadow <elijah.j.winter@outlook.com>"
LABEL description="A Docker container for scraping Wired.com articles"
LABEL version="1.0"