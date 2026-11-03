from ups_kulka.modules.admin_auth.application.public import AdminAuthFacade


class AdminAuthAdapter:
    def __init__(self, auth: AdminAuthFacade) -> None:
        self._auth = auth

    def require_admin(self, token: str | None) -> None:
        self._auth.verify_token(token)
