"""Global mapping of domain errors to HTTP responses.

Routers must not catch DomainError themselves.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ups_kulka.shared.domain.errors import (
    ConflictError,
    DomainError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)

_STATUS_BY_ERROR: tuple[tuple[type[DomainError], int], ...] = (
    (UnauthorizedError, status.HTTP_401_UNAUTHORIZED),
    (NotFoundError, status.HTTP_404_NOT_FOUND),
    (ConflictError, status.HTTP_409_CONFLICT),
    (ValidationError, 422),
)


class ErrorOut(BaseModel):
    code: str
    message: str


def _status_for(error: DomainError) -> int:
    for error_type, http_status in _STATUS_BY_ERROR:
        if isinstance(error, error_type):
            return http_status
    return status.HTTP_400_BAD_REQUEST


async def _handle_domain_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, DomainError)  # noqa: S101 - registered only for DomainError
    body = ErrorOut(code=exc.code, message=exc.message)
    return JSONResponse(status_code=_status_for(exc), content=body.model_dump())


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _handle_domain_error)
