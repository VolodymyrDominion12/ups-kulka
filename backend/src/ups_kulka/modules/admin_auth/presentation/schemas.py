from datetime import datetime

from pydantic import BaseModel, Field

from ups_kulka.modules.admin_auth.application.dto import AdminSessionDTO, LoginAdminCommand


class AdminLoginIn(BaseModel):
    password: str = Field(min_length=1, max_length=200)

    def to_command(self) -> LoginAdminCommand:
        return LoginAdminCommand(password=self.password)


class AdminSessionOut(BaseModel):
    role: str
    token: str
    expires_at: datetime

    @classmethod
    def from_dto(cls, dto: AdminSessionDTO) -> "AdminSessionOut":
        return cls(role=dto.role, token=dto.token, expires_at=dto.expires_at)
