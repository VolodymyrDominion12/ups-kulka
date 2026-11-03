from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="UPS_", extra="ignore")

    environment: str = "local"
    database_url: str = "postgresql+asyncpg://ups:ups@localhost:5432/ups_kulka"
    sql_echo: bool = False

    @property
    def sync_database_url(self) -> str:
        """URL for Alembic (sync psycopg driver)."""
        return self.database_url.replace("+asyncpg", "+psycopg")
