FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8100 \
    RAG_HOST=0.0.0.0 \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    HF_ENDPOINT=https://hf-mirror.com

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 sqlite3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir \
        "sentence-transformers>=3.0.0" \
        "chromadb>=0.5.0" \
        "pysqlite3-binary>=0.5.0" \
        "fastapi>=0.110.0" \
        "uvicorn>=0.27.0" \
        "pydantic>=2.0.0"

COPY *.py ./
COPY data/chroma ./data/chroma

EXPOSE 8100

CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8100"]
