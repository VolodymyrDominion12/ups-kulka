.PHONY: install up down migrate revision run test test-unit test-arch test-int lint format types openapi openapi-check check

install:
	uv sync

up:
	docker compose -f ../deploy/compose.dev.yml up -d

down:
	docker compose -f ../deploy/compose.dev.yml down

migrate:
	uv run alembic upgrade head

# make revision m="add collections"
revision:
	uv run alembic revision --autogenerate -m "$(m)"

run:
	uv run uvicorn ups_kulka.main:app --reload --app-dir src

test:
	uv run pytest --cov --cov-report=term-missing

test-unit:
	uv run pytest tests/unit tests/architecture

test-arch:
	uv run pytest tests/architecture

test-int:
	uv run pytest tests/integration tests/migrations

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

types:
	uv run mypy

openapi:
	uv run python scripts/export_openapi.py

openapi-check:
	uv run python scripts/export_openapi.py --check

check: lint types test openapi-check
