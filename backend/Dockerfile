# ─── BUILDER STAGE ───
FROM python:3.11-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev

# Use a separate layer for heavy ML libraries to benefit from caching and CPU optimizations
# This saves ~600MB and ~5 mins on build because it avoids the full GPU-enabled binaries
RUN pip install --no-cache-dir torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── FINAL STAGE ───
FROM python:3.11-slim
WORKDIR /app

# Only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder to keep final image clean and small
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# Entrypoint setup
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Environment variables for better performance
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "app.main:app", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120"]

