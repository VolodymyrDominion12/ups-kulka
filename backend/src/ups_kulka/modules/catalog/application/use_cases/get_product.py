from ups_kulka.modules.catalog.application.dto import ProductDTO
from ups_kulka.modules.catalog.application.ports import CatalogUnitOfWorkFactory
from ups_kulka.modules.catalog.domain.errors import ProductNotFound


class GetProduct:
    """Public product page: only active products are visible."""

    def __init__(self, uow_factory: CatalogUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self, slug: str) -> ProductDTO:
        async with self._uow_factory() as uow:
            product = await uow.products.get_by_slug(slug, active_only=True)
        if product is None:
            raise ProductNotFound(slug)
        return ProductDTO.from_entity(product)
