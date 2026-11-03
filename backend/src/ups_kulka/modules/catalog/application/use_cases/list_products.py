from ups_kulka.modules.catalog.application.dto import ListProductsQuery, ProductDTO
from ups_kulka.modules.catalog.application.ports import CatalogUnitOfWorkFactory
from ups_kulka.shared.application.pagination import Page, PageRequest


class ListProducts:
    """Storefront list of active products, optionally filtered by a tag."""

    def __init__(self, uow_factory: CatalogUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self, query: ListProductsQuery) -> Page[ProductDTO]:
        page_request = PageRequest(limit=query.limit, offset=query.offset)
        async with self._uow_factory() as uow:
            page = await uow.products.list_active(tag_slug=query.tag_slug, page=page_request)
        return Page(
            items=tuple(ProductDTO.from_entity(product) for product in page.items),
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )
