FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . \
    && mkdir -p /app/data \
    && chown -R app:app /app

ENV PROTOMIND_DATABASE=/app/data/protomind.sqlite3 \
    PROTOMIND_CAPTURE_DIR=/app/data/captures \
    PROTOMIND_RUN_DIR=/app/data/runs

USER app

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["uvicorn", "protomind.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
