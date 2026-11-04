"""In-memory fakes of catalog ports for fast unit tests (no DB)."""

import uuid
from collections.abc import Sequence
from types import TracebackType
from typing import Self

from ups_kulka.modules.catalog.application.dto import ProductForOrder
from ups_kulka.modules.catalog.application.ports import MediaSnapshot
from ups_kulka.modules.catalog.domain.entities import Product, Tag
from ups_kulka.shared.application.pagination import Page, PageRequest


class InMemoryTagRepository:
    def __init__(self, store: dict[str, Tag], products: dict[str, Product]) -> None:
        self._store = store
        self._products = products

    async def add(self, tag: Tag) -> None:
        self._store[tag.slug.value] = tag

    async def save(self, tag: Tag) -> None:
        self._store[tag.slug.value] = tag

    async def slug_exists(self, slug: str) -> bool:
        return slug in self._store

    async def get_by_slugs(self, slugs: Sequence[str]) -> list[Tag]:
        return [self._store[slug] for slug in slugs if slug in self._store]

    async def list_all(self) -> list[Tag]:
        return sorted(self._store.values(), key=lambda t: (t.group.value, t.name))

    def _active_count(self, tag: Tag) -> int:
        return sum(
            1
            for p in self._products.values()
            if p.is_active and any(t.id == tag.id for t in p.tags)
        )

    async def get_by_slug_with_count(self, slug: str) -> tuple[Tag, int] | None:
        tag = self._store.get(slug)
        if tag is None:
            return None
        return tag, self._active_count(tag)

    async def get_by_id_with_count(self, tag_id: uuid.UUID) -> tuple[Tag, int] | None:
        for tag in self._store.values():
            if tag.id == tag_id:
                return tag, self._active_count(tag)
        return None

    async def list_with_counts(self) -> list[tuple[Tag, int]]:
        tags = sorted(self._store.values(), key=lambda t: (t.group.value, t.name))
        return [(tag, self._active_count(tag)) for tag in tags]


class InMemoryProductRepository:
    def __init__(self, store: dict[str, Product]) -> None:
        self._store = store

    async def add(self, product: Product) -> None:
        self._store[product.slug.value] = product

    async def save(self, product: Product) -> None:
        self._store[product.slug.value] = product

    async def slug_exists(self, slug: str) -> bool:
        return slug in self._store

    async def get_by_id(self, product_id: uuid.UUID) -> Product | None:
        for p in self._store.values():
            if p.id == product_id:
                return p
        return None

    async def get_by_slug(self, slug: str, *, active_only: bool = True) -> Product | None:
        product = self._store.get(slug)
        if product is None or (active_only and not product.is_active):
            return None
        return product

    async def list_active(
        self,
        *,
        tag_slug: str | None,
        page: PageRequest,
        q: str | None = None,
        sort: str = "newest",
        on_sale: bool | None = None,
    ) -> Page[Product]:
        def matches(product: Product) -> bool:
            if not product.is_active:
                return False
            if tag_slug is not None and not any(t.slug.value == tag_slug for t in product.tags):
                return False
            if on_sale and product.old_price is None:
                return False
            if q and q.strip():
                needle = q.strip().lower()
                haystack = (
                    product.name.lower()
                    + " "
                    + product.description.lower()
                    + " "
                    + product.slug.value.lower()
                )
                if needle not in haystack:
                    return False
            return True

        items = [p for p in self._store.values() if matches(p)]
        if sort == "price_asc":
            items.sort(key=lambda p: p.price.kopecks)
        elif sort == "price_desc":
            items.sort(key=lambda p: p.price.kopecks, reverse=True)
        else:
            items.sort(key=lambda p: (p.created_at, p.id), reverse=True)
        return Page(
            items=tuple(items[page.offset : page.offset + page.limit]),
            total=len(items),
            limit=page.limit,
            offset=page.offset,
        )

    async def list_for_admin(
        self,
        *,
        q: str | None,
        tag_slug: str | None,
        is_active: bool | None,
        page: PageRequest,
    ) -> Page[Product]:
        items = list(self._store.values())
        if is_active is not None:
            items = [p for p in items if p.is_active == is_active]
        if tag_slug is not None:
            items = [p for p in items if any(t.slug.value == tag_slug for t in p.tags)]
        if q and q.strip():
            needle = q.strip().lower()
            items = [p for p in items if needle in p.name.lower() or needle in p.slug.value.lower()]
        items.sort(key=lambda p: (p.created_at, p.id), reverse=True)
        return Page(
            items=tuple(items[page.offset : page.offset + page.limit]),
            total=len(items),
            limit=page.limit,
            offset=page.offset,
        )

    async def list_all_for_analytics(self) -> list[Product]:
        return list(self._store.values())

    async def get_for_order(self, ids: Sequence[uuid.UUID]) -> list[ProductForOrder]:
        wanted = set(ids)
        return [
            ProductForOrder(
                id=p.id, name=p.name, price_kopecks=p.price.kopecks, is_active=p.is_active
            )
            for p in self._store.values()
            if p.id in wanted
        ]


class FakeMediaLookup:
    def __init__(self, *media_ids: uuid.UUID) -> None:
        self.snapshots: dict[uuid.UUID, MediaSnapshot] = {
            mid: MediaSnapshot(
                media_id=mid,
                url_prefix=f"/media/{mid}",
                blur_data_url="data:image/webp;base64,AAA",
                width=800,
                height=1000,
            )
            for mid in media_ids
        }

    async def get_media_snapshots(self, ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, MediaSnapshot]:
        return {mid: self.snapshots[mid] for mid in ids if mid in self.snapshots}


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
        self.tags = InMemoryTagRepository(self._tags, self._products)
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
