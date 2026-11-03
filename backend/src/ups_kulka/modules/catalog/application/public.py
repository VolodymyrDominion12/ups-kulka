"""Public facade of the catalog module: the ONLY entry point for other modules."""

import uuid
from collections.abc import Sequence

from ups_kulka.modules.catalog.application.dto import (
    ProductAnalyticsInfo,
    ProductForOrder,
    TagDTO,
)
from ups_kulka.modules.catalog.application.ports import CatalogUnitOfWorkFactory

__all__ = ["CatalogFacade", "ProductAnalyticsInfo", "ProductForOrder"]


class CatalogFacade:
    def __init__(self, uow_factory: CatalogUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def products_for_order(
        self, ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, ProductForOrder]:
        """Current name and price of each product, active or not; unknown ids are absent."""
        unique_ids = list(dict.fromkeys(ids))
        async with self._uow_factory() as uow:
            products = await uow.products.get_for_order(unique_ids)
        return {product.id: product for product in products}

    async def products_for_analytics(self) -> list[ProductAnalyticsInfo]:
        """All products with their tags for marketing analytics."""
        async with self._uow_factory() as uow:
            products = await uow.products.list_all_for_analytics()
        return [
            ProductAnalyticsInfo(
                id=p.id,
                slug=p.slug.value,
                name=p.name,
                price_kopecks=p.price.kopecks,
                is_active=p.is_active,
                created_at=p.created_at,
                tags=tuple(TagDTO.from_entity(t) for t in p.tags),
            )
            for p in products
        ]
