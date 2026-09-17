# Nebula Admin — Backend for Frontend (FastAPI)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app

RUN pip install --upgrade pip && pip install .

EXPOSE 8001

# Sobe o BFF na porta do provedor ($PORT). O BFF não acessa banco: ele fala
# com o Core via NEBULA_CORE_BASE_URL / NEBULA_CORE_SERVICE_TOKEN.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
