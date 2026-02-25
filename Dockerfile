FROM python:3.11-slim

# Product metadata labels
LABEL org.opencontainers.image.title="WasteWise"
LABEL org.opencontainers.image.description="Premium eco-app for waste classification, carbon tracking, and green rewards"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="WasteWise Team"
LABEL org.opencontainers.image.vendor="WasteWise"

# Set working directory
WORKDIR /app

# Install system dependencies if needed (e.g., for bcrypt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt
RUN pip install --no-cache-dir gunicorn uvicorn

# Copy backend code
COPY backend/ ./backend/

# Copy frontend static files
# Note: We copy the public folder which is what main.py serves
COPY cinematic-scroll/public/ ./cinematic-scroll/public/

# Expose the port the app runs on
EXPOSE 8000

# Set environment variable for the directory
ENV PYTHONPATH=/app/backend

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
