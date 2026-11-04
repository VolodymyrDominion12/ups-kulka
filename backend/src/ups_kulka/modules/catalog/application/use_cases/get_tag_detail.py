from ups_kulka.modules.catalog.application.dto import TagDetailDTO
from ups_kulka.modules.catalog.application.ports import CatalogUnitOfWorkFactory
from ups_kulka.modules.catalog.domain.errors import TagNotFound


class GetTagDetail:
    """Public collection page data: a tag with its SEO content and product count."""

    def __init__(self, uow_factory: CatalogUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self, slug: str) -> TagDetailDTO:
        async with self._uow_factory() as uow:
            result = await uow.tags.get_by_slug_with_count(slug)
        if result is None:
            raise TagNotFound(slug)
        tag, product_count = result
        return TagDetailDTO.from_entity(tag, product_count)
