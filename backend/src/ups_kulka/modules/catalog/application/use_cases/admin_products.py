"""Admin use cases for the salon express catalog workflow (specs/007-admin)."""

from ups_kulka.modules.catalog.application.dto import (
    ListAdminProductsQuery,
    ProductDTO,
    QuickCreateProductCommand,
    UpdateProductCommand,
)
from ups_kulka.modules.catalog.application.ports import (
    CatalogAdminGuard,
    CatalogUnitOfWork,
    CatalogUnitOfWorkFactory,
    MediaCatalogLookup,
)
from ups_kulka.modules.catalog.application.use_cases.create_product import (
    resolve_product_images,
)
from ups_kulka.modules.catalog.domain.entities import Product, Slug
from ups_kulka.modules.catalog.domain.errors import (
    ProductNotFound,
    SlugAlreadyTaken,
    UnknownTags,
)
from ups_kulka.shared.application.pagination import Page, PageRequest
from ups_kulka.shared.domain.money import Money


async def _pick_unique_slug(uow: CatalogUnitOfWork, name: str, requested_slug: str | None) -> Slug:
    if requested_slug and requested_slug.strip():
        slug = Slug(requested_slug.strip().lower())
        if await uow.products.slug_exists(slug.value):
            raise SlugAlreadyTaken(slug.value)
        return slug

    base = Slug.base_from_name(name)
    candidate = base
    suffix = 2
    while await uow.products.slug_exists(candidate):
        candidate = f"{base[:110]}-{suffix}"
        suffix += 1
    return Slug(candidate)


class QuickCreateProduct:
    """Express product creation from mobile camera in the salon: auto-slug + photos."""

    def __init__(
        self,
        uow_factory: CatalogUnitOfWorkFactory,
        media_lookup: MediaCatalogLookup | None = None,
        auth: CatalogAdminGuard | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._media_lookup = media_lookup
        self._auth = auth

    async def __call__(self, cmd: QuickCreateProductCommand) -> ProductDTO:
        if self._auth is not None:
            self._auth.require_admin(cmd.auth_token)

        requested_tags = list(dict.fromkeys(cmd.tag_slugs))
        images = await resolve_product_images(cmd.media_ids, self._media_lookup)

        async with self._uow_factory() as uow:
            slug = await _pick_unique_slug(uow, cmd.name, cmd.slug)
            tags = await uow.tags.get_by_slugs(requested_tags)
            missing = set(requested_tags) - {tag.slug.value for tag in tags}
            if missing:
                raise UnknownTags(sorted(missing))

            product = Product.create(
                slug=slug.value,
                name=cmd.name,
                description=cmd.description,
                price=Money(cmd.price_kopecks),
                old_price=Money(cmd.old_price_kopecks) if cmd.old_price_kopecks else None,
                is_active=cmd.is_active,
                tags=tuple(tags),
                images=images,
            )
            await uow.products.add(product)
            await uow.commit()

        return ProductDTO.from_entity(product)


class UpdateProduct:
    def __init__(
        self,
        uow_factory: CatalogUnitOfWorkFactory,
        media_lookup: MediaCatalogLookup | None = None,
        auth: CatalogAdminGuard | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._media_lookup = media_lookup
        self._auth = auth

    async def __call__(self, cmd: UpdateProductCommand) -> ProductDTO:
        if self._auth is not None:
            self._auth.require_admin(cmd.auth_token)

        images = (
            await resolve_product_images(cmd.media_ids, self._media_lookup)
            if cmd.media_ids is not None
            else None
        )

        async with self._uow_factory() as uow:
            product = await uow.products.get_by_id(cmd.product_id)
            if product is None:
                raise ProductNotFound(str(cmd.product_id))

            tags_tuple = None
            if cmd.tag_slugs is not None:
                requested_tags = list(dict.fromkeys(cmd.tag_slugs))
                tags = await uow.tags.get_by_slugs(requested_tags)
                missing = set(requested_tags) - {tag.slug.value for tag in tags}
                if missing:
                    raise UnknownTags(sorted(missing))
                tags_tuple = tuple(tags)

            product.update(
                name=cmd.name,
                description=cmd.description,
                price=Money(cmd.price_kopecks) if cmd.price_kopecks is not None else None,
                old_price=(
                    Money(cmd.old_price_kopecks) if cmd.old_price_kopecks is not None else None
                ),
                clear_old_price=cmd.clear_old_price,
                is_active=cmd.is_active,
                tags=tags_tuple,
                images=images,
            )
            await uow.products.save(product)
            await uow.commit()

        return ProductDTO.from_entity(product)


class ListAdminProducts:
    def __init__(
        self,
        uow_factory: CatalogUnitOfWorkFactory,
        auth: CatalogAdminGuard | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._auth = auth

    async def __call__(self, query: ListAdminProductsQuery) -> Page[ProductDTO]:
        if self._auth is not None:
            self._auth.require_admin(query.auth_token)

        page_req = PageRequest(limit=query.limit, offset=query.offset)
        async with self._uow_factory() as uow:
            page = await uow.products.list_for_admin(
                q=query.q,
                tag_slug=query.tag_slug,
                is_active=query.is_active,
                page=page_req,
            )
        return Page(
            items=tuple(ProductDTO.from_entity(p) for p in page.items),
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )
