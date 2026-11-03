import pytest
from pydantic import ValidationError

from ups_kulka.settings import Settings

STRONG_KEY = "k" * 40


def _settings(**values: str) -> Settings:
    return Settings(_env_file=None, **values)  # type: ignore[call-arg]


def test_local_environment_keeps_dev_defaults() -> None:
    settings = _settings(environment="local")
    assert settings.admin_password == "admin123"


@pytest.mark.parametrize("environment", ["production", "staging"])
def test_servers_refuse_dev_admin_secrets(environment: str) -> None:
    with pytest.raises(ValidationError) as exc:
        _settings(environment=environment)
    assert "UPS_ADMIN_PASSWORD" in str(exc.value)
    assert "UPS_ADMIN_SECRET_KEY" in str(exc.value)


def test_servers_refuse_short_secret_key() -> None:
    with pytest.raises(ValidationError, match="UPS_ADMIN_SECRET_KEY"):
        _settings(environment="production", admin_password="Str0ng!", admin_secret_key="short")


def test_servers_start_with_real_secrets() -> None:
    settings = _settings(
        environment="production", admin_password="Str0ng!", admin_secret_key=STRONG_KEY
    )
    assert settings.environment == "production"
