install:
	uv sync --extra dev

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format src tests

run:
	uv run uvicorn protomind.api.main:app --reload
