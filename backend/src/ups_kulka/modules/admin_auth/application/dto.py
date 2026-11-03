from dataclasses import dataclass
from datetime import datetime

from ups_kulka.modules.admin_auth.domain.entities import AdminSession


@dataclass(frozen=True, slots=True)
class LoginAdminCommand:
    password: str


@dataclass(frozen=True, slots=True)
class AdminSessionDTO:
    role: str
    token: str
    expires_at: datetime

    @classmethod
    def from_entity(cls, session: AdminSession) -> "AdminSessionDTO":
        return cls(
            role=session.role.value,
            token=session.token,
            expires_at=session.expires_at,
        )
