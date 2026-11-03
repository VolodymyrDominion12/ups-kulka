"""Ports (interfaces) the catalog use cases depend on.

Implementations live in ``infrastructure``; tests use in-memory fakes.
"""

from collections.abc import Callable, Sequence
from typing import Protocol

from ups_kulka.modules.catalog.domain.entities import Product, Tag
from ups_kulka.shared.application.pagination import Page, PageRequest
from ups_kulka.shared.application.uow import UnitOfWork


class ProductRepository(Protocol):
    async def add(self, product: Product) -> None: ...

    async def slug_exists(self, slug: str) -> bool: ...

    async def get_by_slug(self, slug: str, *, active_only: bool = True) -> Product | None: ...

    async def list_active(self, *, tag_slug: str | None, page: PageRequest) -> Page[Product]:
        """Must run a constant number of queries regardless of page size (no N+1)."""
        ...


class TagRepository(Protocol):
    async def add(self, tag: Tag) -> None: ...

    async def slug_exists(self, slug: str) -> bool: ...

    async def get_by_slugs(self, slugs: Sequence[str]) -> list[Tag]:
        """Batch lookup: one query for any number of slugs."""
        ...


class CatalogUnitOfWork(UnitOfWork, Protocol):
    products: ProductRepository
    tags: TagRepository


type CatalogUnitOfWorkFactory = Callable[[], CatalogUnitOfWork]
