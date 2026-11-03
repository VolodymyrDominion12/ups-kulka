"""Admin authentication HTTP adapter (thin, see backend/AGENTS.md)."""

from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header

from ups_kulka.modules.admin_auth.application.use_cases.login_admin import (
    LoginAdmin,
    VerifyAdminSession,
)
from ups_kulka.modules.admin_auth.presentation.schemas import AdminLoginIn, AdminSessionOut
from ups_kulka.shared.presentation.errors import ErrorOut

router = APIRouter(prefix="/api/v1/admin/auth", tags=["admin-auth"])

_ERRORS: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorOut},
    422: {"model": ErrorOut},
}


@router.post("/login", responses=_ERRORS)
@inject
async def login_admin(
    body: AdminLoginIn,
    use_case: LoginAdmin = Depends(Provide["admin_auth.login_admin"]),
) -> AdminSessionOut:
    return AdminSessionOut.from_dto(await use_case(body.to_command()))


@router.get("/me", responses=_ERRORS)
@inject
async def get_admin_session(
    authorization: Annotated[str | None, Header()] = None,
    use_case: VerifyAdminSession = Depends(Provide["admin_auth.verify_session"]),
) -> AdminSessionOut:
    return AdminSessionOut.from_dto(await use_case(authorization))
