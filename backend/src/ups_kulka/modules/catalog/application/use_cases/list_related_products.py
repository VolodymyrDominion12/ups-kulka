from ups_kulka.modules.catalog.application.dto import ProductDTO
from ups_kulka.modules.catalog.application.ports import CatalogUnitOfWorkFactory
from ups_kulka.modules.catalog.domain.entities import RELATED_PRODUCTS_LIMIT


class ListRelatedProducts:
    """Cross-sell: active products sharing tags with the given product."""

    def __init__(self, uow_factory: CatalogUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self, slug: str) -> list[ProductDTO]:
        async with self._uow_factory() as uow:
            products = await uow.products.list_related(slug, RELATED_PRODUCTS_LIMIT)
        return [ProductDTO.from_entity(product) for product in products]
