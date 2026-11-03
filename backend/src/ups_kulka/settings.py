from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="UPS_", extra="ignore")

    environment: str = "local"
    database_url: str = "postgresql+asyncpg://ups:ups@localhost:5432/ups_kulka"
    sql_echo: bool = False
    # Public URL of the site: payment redirect and webhook addresses are built from it.
    public_base_url: str = "http://localhost:3000"
    # Online payment (specs/006). Empty token = online payment is switched off.
    monobank_token: str = ""
    # Shop notifications (specs/008). Empty = messages go to the log.
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    # Admin panel (specs/007) and media pipeline (specs/009).
    admin_password: str = "admin123"  # noqa: S105 - local dev default
    admin_secret_key: str = "local-dev-secret-change-in-production"  # noqa: S105
    media_root: str = "./var/media"

    @property
    def sync_database_url(self) -> str:
        """URL for Alembic (sync psycopg driver)."""
        return self.database_url.replace("+asyncpg", "+psycopg")
