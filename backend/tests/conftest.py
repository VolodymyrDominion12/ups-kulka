"""Shared fixtures. PostgreSQL comes from TEST_DATABASE_URL (CI service) or a
throwaway testcontainers instance (local Docker). SQLite is not allowed."""

import os
from collections.abc import AsyncIterator, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncEngine

from ups_kulka.db_models import metadata
from ups_kulka.shared.infrastructure.db import create_engine

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _to_async_url(url: str) -> str:
    for driver in ("postgresql+psycopg2://", "postgresql+psycopg://", "postgresql://"):
        if url.startswith(driver):
            return "postgresql+asyncpg://" + url.removeprefix(driver)
    return url


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    env_url = os.environ.get("TEST_DATABASE_URL")
    if env_url:
        yield _to_async_url(env_url)
        return
    try:
        from testcontainers.postgres import PostgresContainer
    except ImportError:  # pragma: no cover
        pytest.skip("Install dev deps or set TEST_DATABASE_URL")
    try:
        container = PostgresContainer("postgres:17-alpine", driver="psycopg")
        container.start()
    except Exception as exc:  # pragma: no cover - no Docker locally
        pytest.fail(
            f"PostgreSQL for tests is not available: start Docker or set TEST_DATABASE_URL ({exc})"
        )
    try:
        yield _to_async_url(container.get_connection_url())
    finally:
        container.stop()


def alembic_config(database_url: str) -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    cfg.attributes["configure_logger"] = False
    return cfg


@pytest.fixture(scope="session")
def migrated_database(database_url: str) -> str:
    command.upgrade(alembic_config(database_url), "head")
    return database_url


@pytest.fixture(scope="session")
async def engine(migrated_database: str) -> AsyncIterator[AsyncEngine]:
    engine = create_engine(migrated_database)
    yield engine
    await engine.dispose()


@pytest.fixture
async def clean_db(engine: AsyncEngine) -> AsyncIterator[None]:
    yield
    tables = ", ".join(f'"{t.name}"' for t in reversed(metadata.sorted_tables))
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


@dataclass
class QueryCounter:
    """Counts SQL statements; use to prove there is no N+1."""

    statements: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.statements)

    def reset(self) -> None:
        self.statements.clear()

    @contextmanager
    def assert_max_queries(self, limit: int) -> Iterator[None]:
        start = len(self.statements)
        yield
        executed = self.statements[start:]
        assert len(executed) <= limit, (
            f"Expected at most {limit} queries, got {len(executed)} (possible N+1):\n"
            + "\n---\n".join(executed)
        )


@pytest.fixture
def query_counter(engine: AsyncEngine) -> Iterator[QueryCounter]:
    counter = QueryCounter()

    def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # type: ignore[no-untyped-def]
        counter.statements.append(statement)

    sync_engine = engine.sync_engine
    event.listen(sync_engine, "before_cursor_execute", _before_cursor_execute)
    try:
        yield counter
    finally:
        event.remove(sync_engine, "before_cursor_execute", _before_cursor_execute)
