FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# pg_isready для ожидания БД
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client && rm -rf /var/lib/apt/lists/*

# чтобы `from app...` работало у alembic
ENV PYTHONPATH=/app

COPY . .

# миграции + запуск API
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-8000}
