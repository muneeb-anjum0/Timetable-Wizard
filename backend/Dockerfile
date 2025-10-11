# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check that uses the runtime PORT (fallback to 5000) and target /api/health
# Give the app more time to start before failing health checks and be more tolerant of transient failures.
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD /bin/sh -c 'curl -f http://localhost:${PORT:-5000}/api/health || exit 1'

# Use gunicorn to serve the minimal WSGI app (simple_app) and log access/errors to stdout
CMD ["/bin/bash", "-lc", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 2 --timeout 30 --access-logfile - --error-logfile - simple_app:app"]