from typing import Protocol

from ups_kulka.modules.admin_auth.domain.entities import AdminSession


class AdminTokenService(Protocol):
    def authenticate_and_issue(self, password: str) -> AdminSession: ...

    def verify(self, token: str | None) -> AdminSession: ...
