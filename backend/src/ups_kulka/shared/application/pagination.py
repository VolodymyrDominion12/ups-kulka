from dataclasses import dataclass

from ups_kulka.shared.domain.errors import ValidationError

DEFAULT_LIMIT = 24
MAX_LIMIT = 100


class InvalidPage(ValidationError):
    code = "invalid_page"


@dataclass(frozen=True, slots=True)
class PageRequest:
    limit: int = DEFAULT_LIMIT
    offset: int = 0

    def __post_init__(self) -> None:
        if not 1 <= self.limit <= MAX_LIMIT:
            raise InvalidPage(f"limit must be between 1 and {MAX_LIMIT}")
        if self.offset < 0:
            raise InvalidPage("offset cannot be negative")


@dataclass(frozen=True, slots=True)
class Page[T]:
    items: tuple[T, ...]
    total: int
    limit: int
    offset: int
