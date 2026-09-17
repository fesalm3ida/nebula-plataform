# Nebula Core — API (FastAPI) + migrations (Alembic)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependências primeiro para aproveitar o cache de camadas.
COPY pyproject.toml README.md ./
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./

RUN pip install --upgrade pip && pip install .

EXPOSE 8000

# Aplica as migrations e sobe a API na porta do provedor ($PORT).
# As configurações vêm de variáveis de ambiente (DATABASE_URL, JWT_SECRET_KEY,
# ADMIN_API_KEY, MERCADOPAGO_*, ...).
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
