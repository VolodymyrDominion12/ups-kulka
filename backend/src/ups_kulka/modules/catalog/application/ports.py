"""Ports (interfaces) the catalog use cases depend on.

Implementations live in ``infrastructure``; tests use in-memory fakes.
"""

import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol

from ups_kulka.modules.catalog.application.dto import ProductForOrder
from ups_kulka.modules.catalog.domain.entities import Product, Tag
from ups_kulka.shared.application.pagination import Page, PageRequest
from ups_kulka.shared.application.uow import UnitOfWork


@dataclass(frozen=True, slots=True)
class MediaSnapshot:
    media_id: uuid.UUID
    url_prefix: str
    blur_data_url: str
    width: int
    height: int


class CatalogAdminGuard(Protocol):
    def require_admin(self, token: str | None) -> None: ...


class MediaCatalogLookup(Protocol):
    async def get_media_snapshots(
        self, ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, MediaSnapshot]: ...


class ProductRepository(Protocol):
    async def add(self, product: Product) -> None: ...

    async def save(self, product: Product) -> None: ...

    async def slug_exists(self, slug: str) -> bool: ...

    async def get_by_id(self, product_id: uuid.UUID) -> Product | None: ...

    async def get_by_slug(self, slug: str, *, active_only: bool = True) -> Product | None: ...

    async def list_active(self, *, tag_slug: str | None, page: PageRequest) -> Page[Product]:
        """Must run a constant number of queries regardless of page size (no N+1)."""
        ...

    async def list_for_admin(
        self,
        *,
        q: str | None,
        tag_slug: str | None,
        is_active: bool | None,
        page: PageRequest,
    ) -> Page[Product]:
        """Must run a constant number of queries regardless of page size (no N+1)."""
        ...

    async def list_all_for_analytics(self) -> list[Product]:
        """Batch fetch products with tags for marketing analytics."""
        ...

    async def get_for_order(self, ids: Sequence[uuid.UUID]) -> list[ProductForOrder]:
        """Batch lookup for checkout: ONE query for any number of ids."""
        ...


class TagRepository(Protocol):
    async def add(self, tag: Tag) -> None: ...

    async def slug_exists(self, slug: str) -> bool: ...

    async def get_by_slugs(self, slugs: Sequence[str]) -> list[Tag]:
        """Batch lookup: one query for any number of slugs."""
        ...

    async def list_all(self) -> list[Tag]: ...


class CatalogUnitOfWork(UnitOfWork, Protocol):
    products: ProductRepository
    tags: TagRepository


type CatalogUnitOfWorkFactory = Callable[[], CatalogUnitOfWork]
