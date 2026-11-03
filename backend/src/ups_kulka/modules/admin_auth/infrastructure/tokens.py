import base64
import hashlib
import hmac
import json
import secrets
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from ups_kulka.modules.admin_auth.domain.entities import AdminRole, AdminSession
from ups_kulka.modules.admin_auth.domain.errors import (
    AdminSessionInvalid,
    InvalidAdminCredentials,
)

SESSION_TTL_DAYS = 30


def _utc_now() -> datetime:
    return datetime.now(UTC)


class HmacAdminTokenService:
    """Stateless HMAC-SHA256 signed token service for single-role salon admin."""

    def __init__(
        self,
        admin_password: str,
        secret_key: str,
        now: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._password = admin_password
        self._secret = secret_key.encode("utf-8")
        self._now = now

    def authenticate_and_issue(self, password: str) -> AdminSession:
        if not self._password or not secrets.compare_digest(password, self._password):
            raise InvalidAdminCredentials

        expires_at = self._now() + timedelta(days=SESSION_TTL_DAYS)
        payload = {
            "role": AdminRole.ADMIN.value,
            "exp": int(expires_at.timestamp()),
        }
        raw_payload = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        b64_payload = base64.urlsafe_b64encode(raw_payload).rstrip(b"=").decode("ascii")
        sig = self._sign(b64_payload)
        token = f"{b64_payload}.{sig}"
        return AdminSession(role=AdminRole.ADMIN, token=token, expires_at=expires_at)

    def verify(self, token: str | None) -> AdminSession:
        if not token or "." not in token:
            raise AdminSessionInvalid
        clean = token.removeprefix("Bearer ").strip()
        parts = clean.split(".")
        if len(parts) != 2:
            raise AdminSessionInvalid
        b64_payload, sig = parts
        expected_sig = self._sign(b64_payload)
        if not secrets.compare_digest(sig, expected_sig):
            raise AdminSessionInvalid

        try:
            padded = b64_payload + "=" * (-len(b64_payload) % 4)
            data = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
            exp = int(data["exp"])
            role = AdminRole(data["role"])
        except (ValueError, KeyError, TypeError) as exc:
            raise AdminSessionInvalid from exc

        now_ts = int(self._now().timestamp())
        if exp <= now_ts:
            raise AdminSessionInvalid

        expires_at = datetime.fromtimestamp(exp, tz=UTC)
        return AdminSession(role=role, token=clean, expires_at=expires_at)

    def _sign(self, b64_payload: str) -> str:
        digest = hmac.new(self._secret, b64_payload.encode("ascii"), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
