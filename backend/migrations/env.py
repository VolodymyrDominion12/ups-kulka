"""Alembic environment. Runs migrations with the sync psycopg driver.

The database URL comes from `sqlalchemy.url` set by the caller (tests) or
from Settings (UPS_DATABASE_URL).
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from ups_kulka.db_models import metadata
from ups_kulka.settings import Settings

config = context.config
if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name)

target_metadata = metadata


def _database_url() -> str:
    url = config.get_main_option("sqlalchemy.url")
    if url:
        return url.replace("+asyncpg", "+psycopg")
    return Settings().sync_database_url


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(_database_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
