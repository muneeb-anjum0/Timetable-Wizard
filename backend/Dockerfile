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

# Health check that uses the runtime PORT (fallback to 5000)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD /bin/sh -c 'curl -f http://localhost:${PORT:-5000}/ || exit 1'

# Simple startup - run fallback simple_app directly (avoids startCommand expansion issues)
CMD ["python", "simple_app.py"]