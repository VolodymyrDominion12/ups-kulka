from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class AdminRole(StrEnum):
    ADMIN = "admin"


@dataclass(frozen=True, slots=True)
class AdminSession:
    role: AdminRole
    token: str
    expires_at: datetime
