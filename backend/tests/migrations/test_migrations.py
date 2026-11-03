"""Schema safety: migrations are reversible, match the ORM, and every FK has an index."""

import pytest
from alembic import command
from sqlalchemy import create_engine, text

from tests.conftest import alembic_config

pytestmark = pytest.mark.integration

# A FK is "indexed" when some index starts with exactly the FK columns (any order).
FK_WITHOUT_INDEX_SQL = text(
    """
    SELECT c.conrelid::regclass::text AS table_name,
           c.conname AS constraint_name,
           pg_get_constraintdef(c.oid) AS definition
    FROM pg_constraint c
    WHERE c.contype = 'f'
      AND c.connamespace = 'public'::regnamespace
      AND NOT EXISTS (
          SELECT 1
          FROM pg_index i
          WHERE i.indrelid = c.conrelid
            AND (i.indkey::int2[])[0:cardinality(c.conkey) - 1] @> c.conkey
            AND (i.indkey::int2[])[0:cardinality(c.conkey) - 1] <@ c.conkey
      )
    ORDER BY 1, 2
    """
)


def _sync_url(url: str) -> str:
    return url.replace("+asyncpg", "+psycopg")


def test_migrations_upgrade_downgrade_upgrade(migrated_database: str) -> None:
    cfg = alembic_config(migrated_database)
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")


def test_models_match_migrations(migrated_database: str) -> None:
    """Fails if someone changed ORM tables without a migration."""
    command.check(alembic_config(migrated_database))


def test_foreign_keys_are_indexed(migrated_database: str) -> None:
    engine = create_engine(_sync_url(migrated_database))
    try:
        with engine.connect() as conn:
            missing = conn.execute(FK_WITHOUT_INDEX_SQL).all()
    finally:
        engine.dispose()
    assert not missing, "Foreign keys without an index:\n" + "\n".join(
        f"  {row.table_name}.{row.constraint_name}: {row.definition}" for row in missing
    )
