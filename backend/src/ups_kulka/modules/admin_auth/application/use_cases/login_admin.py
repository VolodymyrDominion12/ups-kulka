from ups_kulka.modules.admin_auth.application.dto import AdminSessionDTO, LoginAdminCommand
from ups_kulka.modules.admin_auth.application.ports import AdminTokenService


class LoginAdmin:
    def __init__(self, tokens: AdminTokenService) -> None:
        self._tokens = tokens

    async def __call__(self, cmd: LoginAdminCommand) -> AdminSessionDTO:
        session = self._tokens.authenticate_and_issue(cmd.password)
        return AdminSessionDTO.from_entity(session)


class VerifyAdminSession:
    def __init__(self, tokens: AdminTokenService) -> None:
        self._tokens = tokens

    async def __call__(self, token: str | None) -> AdminSessionDTO:
        session = self._tokens.verify(token)
        return AdminSessionDTO.from_entity(session)
