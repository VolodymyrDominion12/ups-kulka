from ups_kulka.shared.domain.errors import UnauthorizedError


class InvalidAdminCredentials(UnauthorizedError):
    code = "invalid_admin_credentials"

    def __init__(self) -> None:
        super().__init__("Невірний пароль адміністратора")


class AdminSessionInvalid(UnauthorizedError):
    code = "unauthorized"

    def __init__(self) -> None:
        super().__init__("Потрібна авторизація адміністратора")
