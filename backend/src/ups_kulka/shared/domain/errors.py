"""Base domain errors.

Presentation maps these to HTTP status codes globally, so use cases and
routers never translate errors by hand.
"""


class DomainError(Exception):
    """Base class for all business-rule violations."""

    code: str = "domain_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    code = "not_found"


class ConflictError(DomainError):
    code = "conflict"


class ValidationError(DomainError):
    code = "validation_error"
