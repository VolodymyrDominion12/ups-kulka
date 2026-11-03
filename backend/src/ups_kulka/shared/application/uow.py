from types import TracebackType
from typing import Protocol, Self


class UnitOfWork(Protocol):
    """One business transaction.

    Use cases open it with ``async with``, call ``commit()`` explicitly;
    leaving the block without commit rolls everything back.
    Each module extends it with its own repositories.
    """

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
