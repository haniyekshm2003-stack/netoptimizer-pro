# =============================================================================
# NetOptimizer Pro - Docker Container for Google Cloud Run
# =============================================================================

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libffi-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/data

EXPOSE 8080
ENV PORT=8080
ENV HOST=0.0.0.0

CMD uvicorn main:app --host $HOST --port $PORT
