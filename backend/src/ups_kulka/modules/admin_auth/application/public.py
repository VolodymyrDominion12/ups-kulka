"""Public facade of admin_auth so other modules can verify admin tokens."""

from ups_kulka.modules.admin_auth.application.dto import AdminSessionDTO
from ups_kulka.modules.admin_auth.application.ports import AdminTokenService

__all__ = ["AdminAuthFacade", "AdminSessionDTO"]


class AdminAuthFacade:
    def __init__(self, tokens: AdminTokenService) -> None:
        self._tokens = tokens

    def verify_token(self, token: str | None) -> AdminSessionDTO:
        session = self._tokens.verify(token)
        return AdminSessionDTO.from_entity(session)
