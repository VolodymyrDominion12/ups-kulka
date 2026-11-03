import uuid
from collections.abc import Sequence

from sqlalchemy import ColumnElement, delete, exists, func, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ups_kulka.modules.catalog.application.dto import ProductForOrder
from ups_kulka.modules.catalog.domain.entities import Product, Tag
from ups_kulka.modules.catalog.infrastructure.mappers import product_to_domain, tag_to_domain
from ups_kulka.modules.catalog.infrastructure.tables import (
    ProductMediaRow,
    ProductRow,
    TagRow,
    product_tags,
)
from ups_kulka.shared.application.pagination import Page, PageRequest


class SqlAlchemyTagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, tag: Tag) -> None:
        self._session.add(
            TagRow(id=tag.id, group=tag.group.value, slug=tag.slug.value, name=tag.name)
        )
        await self._session.flush()

    async def slug_exists(self, slug: str) -> bool:
        stmt = select(exists().where(TagRow.slug == slug))
        return bool(await self._session.scalar(stmt))

    async def get_by_slugs(self, slugs: Sequence[str]) -> list[Tag]:
        if not slugs:
            return []
        rows = await self._session.scalars(select(TagRow).where(TagRow.slug.in_(slugs)))
        return [tag_to_domain(row) for row in rows]

    async def list_all(self) -> list[Tag]:
        rows = await self._session.scalars(select(TagRow).order_by(TagRow.group, TagRow.name))
        return [tag_to_domain(row) for row in rows]


class SqlAlchemyProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, product: Product) -> None:
        self._session.add(
            ProductRow(
                id=product.id,
                slug=product.slug.value,
                name=product.name,
                description=product.description,
                price_kopecks=product.price.kopecks,
                old_price_kopecks=product.old_price.kopecks if product.old_price else None,
                is_active=product.is_active,
                created_at=product.created_at,
                updated_at=product.updated_at or product.created_at,
            )
        )
        await self._session.flush()
        if product.tags:
            await self._session.execute(
                insert(product_tags),
                [{"product_id": product.id, "tag_id": tag.id} for tag in product.tags],
            )
        if product.images:
            await self._session.execute(
                insert(ProductMediaRow),
                [
                    {
                        "product_id": product.id,
                        "position": img.position,
                        "media_id": img.media_id,
                        "url_prefix": img.url_prefix,
                        "blur_data_url": img.blur_data_url,
                        "width": img.width,
                        "height": img.height,
                    }
                    for img in product.images
                ],
            )

    async def save(self, product: Product) -> None:
        await self._session.execute(
            update(ProductRow)
            .where(ProductRow.id == product.id)
            .values(
                name=product.name,
                description=product.description,
                price_kopecks=product.price.kopecks,
                old_price_kopecks=product.old_price.kopecks if product.old_price else None,
                is_active=product.is_active,
                updated_at=product.updated_at or product.created_at,
            )
        )
        await self._session.execute(
            delete(product_tags).where(product_tags.c.product_id == product.id)
        )
        if product.tags:
            await self._session.execute(
                insert(product_tags),
                [{"product_id": product.id, "tag_id": tag.id} for tag in product.tags],
            )
        await self._session.execute(
            delete(ProductMediaRow).where(ProductMediaRow.product_id == product.id)
        )
        if product.images:
            await self._session.execute(
                insert(ProductMediaRow),
                [
                    {
                        "product_id": product.id,
                        "position": img.position,
                        "media_id": img.media_id,
                        "url_prefix": img.url_prefix,
                        "blur_data_url": img.blur_data_url,
                        "width": img.width,
                        "height": img.height,
                    }
                    for img in product.images
                ],
            )

    async def slug_exists(self, slug: str) -> bool:
        stmt = select(exists().where(ProductRow.slug == slug))
        return bool(await self._session.scalar(stmt))

    async def get_by_id(self, product_id: uuid.UUID) -> Product | None:
        stmt = (
            select(ProductRow)
            .options(selectinload(ProductRow.tags), selectinload(ProductRow.media))
            .where(ProductRow.id == product_id)
        )
        row = await self._session.scalar(stmt)
        return product_to_domain(row) if row is not None else None

    async def get_by_slug(self, slug: str, *, active_only: bool = True) -> Product | None:
        stmt = (
            select(ProductRow)
            .options(selectinload(ProductRow.tags), selectinload(ProductRow.media))
            .where(ProductRow.slug == slug)
        )
        if active_only:
            stmt = stmt.where(ProductRow.is_active.is_(True))
        row = await self._session.scalar(stmt)
        return product_to_domain(row) if row is not None else None

    async def list_active(self, *, tag_slug: str | None, page: PageRequest) -> Page[Product]:
        """Constant queries: count, page of products, selectinload(tags), selectinload(media)."""
        conditions: list[ColumnElement[bool]] = [ProductRow.is_active.is_(True)]
        if tag_slug is not None:
            conditions.append(
                exists()
                .where(product_tags.c.product_id == ProductRow.id)
                .where(product_tags.c.tag_id == TagRow.id)
                .where(TagRow.slug == tag_slug)
            )
        return await self._paginate(conditions, page)

    async def list_for_admin(
        self,
        *,
        q: str | None,
        tag_slug: str | None,
        is_active: bool | None,
        page: PageRequest,
    ) -> Page[Product]:
        conditions: list[ColumnElement[bool]] = []
        if is_active is not None:
            conditions.append(ProductRow.is_active.is_(is_active))
        if tag_slug is not None:
            conditions.append(
                exists()
                .where(product_tags.c.product_id == ProductRow.id)
                .where(product_tags.c.tag_id == TagRow.id)
                .where(TagRow.slug == tag_slug)
            )
        if q and q.strip():
            pattern = f"%{q.strip()}%"
            conditions.append(or_(ProductRow.name.ilike(pattern), ProductRow.slug.ilike(pattern)))
        return await self._paginate(conditions, page)

    async def list_all_for_analytics(self) -> list[Product]:
        rows = await self._session.scalars(
            select(ProductRow).options(
                selectinload(ProductRow.tags),
                selectinload(ProductRow.media),
            )
        )
        return [product_to_domain(row) for row in rows]

    async def get_for_order(self, ids: Sequence[uuid.UUID]) -> list[ProductForOrder]:
        if not ids:
            return []
        rows = await self._session.execute(
            select(
                ProductRow.id, ProductRow.name, ProductRow.price_kopecks, ProductRow.is_active
            ).where(ProductRow.id.in_(ids))
        )
        return [
            ProductForOrder(
                id=r.id, name=r.name, price_kopecks=r.price_kopecks, is_active=r.is_active
            )
            for r in rows
        ]

    async def _paginate(
        self, conditions: list[ColumnElement[bool]], page: PageRequest
    ) -> Page[Product]:
        total = await self._session.scalar(
            select(func.count()).select_from(ProductRow).where(*conditions)
        )
        rows = await self._session.scalars(
            select(ProductRow)
            .options(selectinload(ProductRow.tags), selectinload(ProductRow.media))
            .where(*conditions)
            .order_by(ProductRow.created_at.desc(), ProductRow.id.desc())
            .limit(page.limit)
            .offset(page.offset)
        )
        return Page(
            items=tuple(product_to_domain(row) for row in rows),
            total=total or 0,
            limit=page.limit,
            offset=page.offset,
        )
