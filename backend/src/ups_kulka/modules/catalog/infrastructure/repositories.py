import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import ColumnElement, Select, delete, exists, func, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ups_kulka.modules.catalog.application.dto import ProductForOrder
from ups_kulka.modules.catalog.domain.entities import Product, ProductSort, Tag
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

    @staticmethod
    def _faq_payload(tag: Tag) -> list[dict[str, str]]:
        return [{"question": item.question, "answer": item.answer} for item in tag.faq]

    async def add(self, tag: Tag) -> None:
        self._session.add(
            TagRow(
                id=tag.id,
                group=tag.group.value,
                slug=tag.slug.value,
                name=tag.name,
                seo_title=tag.seo_title,
                seo_description=tag.seo_description,
                intro_text=tag.intro_text,
                seo_text=tag.seo_text,
                faq=self._faq_payload(tag),
            )
        )
        await self._session.flush()

    async def save(self, tag: Tag) -> None:
        await self._session.execute(
            update(TagRow)
            .where(TagRow.id == tag.id)
            .values(
                seo_title=tag.seo_title,
                seo_description=tag.seo_description,
                intro_text=tag.intro_text,
                seo_text=tag.seo_text,
                faq=self._faq_payload(tag),
            )
        )

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

    def _count_query(self) -> Select[TagRow, int]:
        """Tag + its active product count in ONE grouped query (no N+1)."""
        return (
            select(TagRow, func.count(ProductRow.id))
            .outerjoin(product_tags, product_tags.c.tag_id == TagRow.id)
            .outerjoin(
                ProductRow,
                (ProductRow.id == product_tags.c.product_id) & ProductRow.is_active.is_(True),
            )
            .group_by(TagRow.id)
        )

    async def get_by_slug_with_count(self, slug: str) -> tuple[Tag, int] | None:
        row = (await self._session.execute(self._count_query().where(TagRow.slug == slug))).first()
        if row is None:
            return None
        tag_row, count = row
        return tag_to_domain(tag_row), count or 0

    async def get_by_id_with_count(self, tag_id: uuid.UUID) -> tuple[Tag, int] | None:
        row = (await self._session.execute(self._count_query().where(TagRow.id == tag_id))).first()
        if row is None:
            return None
        tag_row, count = row
        return tag_to_domain(tag_row), count or 0

    async def list_with_counts(self) -> list[tuple[Tag, int]]:
        rows = await self._session.execute(self._count_query().order_by(TagRow.group, TagRow.name))
        return [(tag_to_domain(tag_row), count or 0) for tag_row, count in rows]


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

    async def list_active(
        self,
        *,
        tag_slug: str | None,
        page: PageRequest,
        q: str | None = None,
        sort: str = "newest",
        on_sale: bool | None = None,
    ) -> Page[Product]:
        """Constant queries: count, page of products, selectinload(tags), selectinload(media)."""
        conditions: list[ColumnElement[bool]] = [ProductRow.is_active.is_(True)]
        if tag_slug is not None:
            conditions.append(
                exists()
                .where(product_tags.c.product_id == ProductRow.id)
                .where(product_tags.c.tag_id == TagRow.id)
                .where(TagRow.slug == tag_slug)
            )
        if q and q.strip():
            pattern = f"%{q.strip()}%"
            conditions.append(
                or_(
                    ProductRow.name.ilike(pattern),
                    ProductRow.description.ilike(pattern),
                    ProductRow.slug.ilike(pattern),
                )
            )
        if on_sale:
            conditions.append(ProductRow.old_price_kopecks.is_not(None))
        return await self._paginate(conditions, page, sort=sort)

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

    async def list_related(self, slug: str, limit: int) -> list[Product]:
        """Active products sharing tags with `slug`, most shared first, then newest."""
        related_tag_ids = (
            select(product_tags.c.tag_id)
            .join(ProductRow, ProductRow.id == product_tags.c.product_id)
            .where(ProductRow.slug == slug)
        )
        shared = func.count(product_tags.c.tag_id)
        id_rows = await self._session.execute(
            select(ProductRow.id, shared.label("shared"))
            .join(product_tags, product_tags.c.product_id == ProductRow.id)
            .where(
                ProductRow.is_active.is_(True),
                ProductRow.slug != slug,
                product_tags.c.tag_id.in_(related_tag_ids),
            )
            .group_by(ProductRow.id)
            .order_by(shared.desc(), ProductRow.created_at.desc(), ProductRow.id.desc())
            .limit(limit)
        )
        ordered_ids = [row.id for row in id_rows]
        if not ordered_ids:
            return []
        rows = await self._session.scalars(
            select(ProductRow)
            .options(selectinload(ProductRow.tags), selectinload(ProductRow.media))
            .where(ProductRow.id.in_(ordered_ids))
        )
        by_id = {row.id: product_to_domain(row) for row in rows}
        return [by_id[pid] for pid in ordered_ids if pid in by_id]

    async def _paginate(
        self,
        conditions: list[ColumnElement[bool]],
        page: PageRequest,
        sort: str = "newest",
    ) -> Page[Product]:
        total = await self._session.scalar(
            select(func.count()).select_from(ProductRow).where(*conditions)
        )
        if sort == ProductSort.PRICE_ASC.value:
            order: list[ColumnElement[Any]] = [
                ProductRow.price_kopecks.asc(),
                ProductRow.id.desc(),
            ]
        elif sort == ProductSort.PRICE_DESC.value:
            order = [ProductRow.price_kopecks.desc(), ProductRow.id.desc()]
        else:
            order = [ProductRow.created_at.desc(), ProductRow.id.desc()]
        rows = await self._session.scalars(
            select(ProductRow)
            .options(selectinload(ProductRow.tags), selectinload(ProductRow.media))
            .where(*conditions)
            .order_by(*order)
            .limit(page.limit)
            .offset(page.offset)
        )
        return Page(
            items=tuple(product_to_domain(row) for row in rows),
            total=total or 0,
            limit=page.limit,
            offset=page.offset,
        )
