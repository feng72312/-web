FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8100 \
    RAG_HOST=0.0.0.0 \
    RAG_CHROMA_DIR=/mnt/chroma \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    HF_ENDPOINT=https://hf-mirror.com

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-server.txt .
RUN pip install --no-cache-dir torch==2.12.1+cpu --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements-server.txt

COPY *.py ./

EXPOSE 8100

CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8100"]
