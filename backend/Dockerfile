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

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD sh -c 'PORT=${PORT:-5000} && curl -f http://localhost:$PORT/api/health || exit 1'

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Starting Flask application..."\n\
echo "Environment variables:" \n\
echo "SUPABASE_URL: $SUPABASE_URL" \n\
echo "SUPABASE_SERVICE_KEY: $(if [ -n "$SUPABASE_SERVICE_KEY" ]; then echo "SET"; else echo "NOT SET"; fi)" \n\
echo "TZ: $TZ" \n\
echo "PORT: ${PORT:-5000}" \n\
PORT=${PORT:-5000} \n\
echo "Using PORT: $PORT" \n\
echo "Testing Python import..."\n\
python -c "import sys; print(f\"Python version: {sys.version}\"); import app; print(\"App imported successfully\")" || { echo "Failed to import app"; exit 1; }\n\
echo "Starting gunicorn..."\n\
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 30 --keep-alive 2 --log-level info --access-logfile - --error-logfile - app:app' > /app/start.sh && chmod +x /app/start.sh

# Start the application
CMD ["/app/start.sh"]