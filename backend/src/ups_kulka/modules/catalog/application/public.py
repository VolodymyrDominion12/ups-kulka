"""Public facade of the catalog module: the ONLY entry point for other modules."""

import uuid
from collections.abc import Sequence

from ups_kulka.modules.catalog.application.dto import ProductForOrder
from ups_kulka.modules.catalog.application.ports import CatalogUnitOfWorkFactory

__all__ = ["CatalogFacade", "ProductForOrder"]


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
