FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY protomind ./protomind
RUN pip install --no-cache-dir .
ENV PROTOMIND_DATABASE=/app/data/protomind.sqlite3 PROTOMIND_CAPTURE_DIR=/app/data/captures PROTOMIND_RUN_DIR=/app/data/runs
EXPOSE 8000
CMD ["uvicorn", "protomind.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
