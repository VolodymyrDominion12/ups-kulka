from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_ADMIN_PASSWORD = "admin123"  # noqa: S105 - local dev default, refused on servers
DEV_ADMIN_SECRET_KEY = "local-dev-secret-change-in-production"  # noqa: S105
SERVER_ENVIRONMENTS = frozenset({"production", "staging"})
MIN_SECRET_KEY_LENGTH = 32


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
    admin_password: str = DEV_ADMIN_PASSWORD
    admin_secret_key: str = DEV_ADMIN_SECRET_KEY
    media_root: str = "./var/media"

    @model_validator(mode="after")
    def _refuse_dev_secrets_on_servers(self) -> Self:
        """Staging and production must not start with the well-known dev admin secrets."""
        if self.environment not in SERVER_ENVIRONMENTS:
            return self
        problems: list[str] = []
        if self.admin_password == DEV_ADMIN_PASSWORD:
            problems.append("UPS_ADMIN_PASSWORD")
        if (
            self.admin_secret_key == DEV_ADMIN_SECRET_KEY
            or len(self.admin_secret_key) < MIN_SECRET_KEY_LENGTH
        ):
            problems.append(f"UPS_ADMIN_SECRET_KEY (min {MIN_SECRET_KEY_LENGTH} chars)")
        if problems:
            raise ValueError(f"set real values on {self.environment}: {', '.join(problems)}")
        return self

    @property
    def sync_database_url(self) -> str:
        """URL for Alembic (sync psycopg driver)."""
        return self.database_url.replace("+asyncpg", "+psycopg")
