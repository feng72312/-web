FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BAZI_DEBUG=false \
    BAZI_KNOWLEDGE_DATA_DIR=/app/knowledge/data \
    BAZI_STATS_DB_PATH=/mnt/data/usage_stats.db \
    BAZI_QUOTA_DB_PATH=/mnt/data/quota.db \
    PORT=8080

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY knowledge/data ./knowledge/data
COPY backend/data/zhuge_qian.json backend/data/zhuge_strokes.json \
     backend/data/jiemeng_entries.json backend/data/shuowen_entries.json \
     backend/data/naming_strokes.json ./app/data/

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--loop", "asyncio"]
