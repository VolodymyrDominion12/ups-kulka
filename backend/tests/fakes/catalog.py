"""In-memory fakes of catalog ports for fast unit tests (no DB)."""

import uuid
from collections.abc import Sequence
from types import TracebackType
from typing import Self

from ups_kulka.modules.catalog.application.dto import ProductForOrder
from ups_kulka.modules.catalog.domain.entities import Product, Tag
from ups_kulka.shared.application.pagination import Page, PageRequest


class InMemoryTagRepository:
    def __init__(self, store: dict[str, Tag]) -> None:
        self._store = store

    async def add(self, tag: Tag) -> None:
        self._store[tag.slug.value] = tag

    async def slug_exists(self, slug: str) -> bool:
        return slug in self._store

    async def get_by_slugs(self, slugs: Sequence[str]) -> list[Tag]:
        return [self._store[slug] for slug in slugs if slug in self._store]


class InMemoryProductRepository:
    def __init__(self, store: dict[str, Product]) -> None:
        self._store = store

    async def add(self, product: Product) -> None:
        self._store[product.slug.value] = product

    async def slug_exists(self, slug: str) -> bool:
        return slug in self._store

    async def get_by_slug(self, slug: str, *, active_only: bool = True) -> Product | None:
        product = self._store.get(slug)
        if product is None or (active_only and not product.is_active):
            return None
        return product

    async def list_active(self, *, tag_slug: str | None, page: PageRequest) -> Page[Product]:
        items = [
            p
            for p in self._store.values()
            if p.is_active and (tag_slug is None or any(t.slug.value == tag_slug for t in p.tags))
        ]
        items.sort(key=lambda p: (p.created_at, p.id), reverse=True)
        return Page(
            items=tuple(items[page.offset : page.offset + page.limit]),
            total=len(items),
            limit=page.limit,
            offset=page.offset,
        )

    async def get_for_order(self, ids: Sequence[uuid.UUID]) -> list[ProductForOrder]:
        wanted = set(ids)
        return [
            ProductForOrder(
                id=p.id, name=p.name, price_kopecks=p.price.kopecks, is_active=p.is_active
            )
            for p in self._store.values()
            if p.id in wanted
        ]


class FakeCatalogUnitOfWork:
    """Data is visible to other UoWs only after commit(), like a real transaction."""

    def __init__(self) -> None:
        self.committed_products: dict[str, Product] = {}
        self.committed_tags: dict[str, Tag] = {}
        self.commits = 0

    def __call__(self) -> Self:
        return self

    async def __aenter__(self) -> Self:
        self._products = dict(self.committed_products)
        self._tags = dict(self.committed_tags)
        self.products = InMemoryProductRepository(self._products)
        self.tags = InMemoryTagRepository(self._tags)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    async def commit(self) -> None:
        self.committed_products = dict(self._products)
        self.committed_tags = dict(self._tags)
        self.commits += 1

    async def rollback(self) -> None:
        return None
