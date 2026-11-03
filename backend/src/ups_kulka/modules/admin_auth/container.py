from dependency_injector import containers, providers

from ups_kulka.modules.admin_auth.application.public import AdminAuthFacade
from ups_kulka.modules.admin_auth.application.use_cases.login_admin import (
    LoginAdmin,
    VerifyAdminSession,
)
from ups_kulka.modules.admin_auth.infrastructure.tokens import HmacAdminTokenService


class AdminAuthContainer(containers.DeclarativeContainer):
    admin_password = providers.Dependency(instance_of=str)
    admin_secret_key = providers.Dependency(instance_of=str)

    token_service = providers.Singleton(
        HmacAdminTokenService,
        admin_password=admin_password,
        secret_key=admin_secret_key,
    )
    login_admin = providers.Factory(LoginAdmin, tokens=token_service)
    verify_session = providers.Factory(VerifyAdminSession, tokens=token_service)
    facade = providers.Factory(AdminAuthFacade, tokens=token_service)
