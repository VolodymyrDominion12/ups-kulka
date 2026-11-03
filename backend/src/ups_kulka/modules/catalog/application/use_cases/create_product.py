import uuid
from collections.abc import Sequence

from ups_kulka.modules.catalog.application.dto import CreateProductCommand, ProductDTO
from ups_kulka.modules.catalog.application.ports import (
    CatalogUnitOfWorkFactory,
    MediaCatalogLookup,
)
from ups_kulka.modules.catalog.domain.entities import Product, ProductImage, Slug
from ups_kulka.modules.catalog.domain.errors import (
    SlugAlreadyTaken,
    UnknownMediaAssets,
    UnknownTags,
)
from ups_kulka.shared.domain.money import Money


async def resolve_product_images(
    media_ids: Sequence[uuid.UUID],
    media_lookup: MediaCatalogLookup | None,
) -> tuple[ProductImage, ...]:
    unique_ids = list(dict.fromkeys(media_ids))
    if not unique_ids:
        return ()
    if media_lookup is None:
        raise UnknownMediaAssets([str(mid) for mid in unique_ids])

    snapshots = await media_lookup.get_media_snapshots(unique_ids)
    missing = [str(mid) for mid in unique_ids if mid not in snapshots]
    if missing:
        raise UnknownMediaAssets(missing)

    return tuple(
        ProductImage(
            media_id=mid,
            position=idx,
            url_prefix=snapshots[mid].url_prefix,
            blur_data_url=snapshots[mid].blur_data_url,
            width=snapshots[mid].width,
            height=snapshots[mid].height,
        )
        for idx, mid in enumerate(unique_ids)
    )


class CreateProduct:
    def __init__(
        self,
        uow_factory: CatalogUnitOfWorkFactory,
        media_lookup: MediaCatalogLookup | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._media_lookup = media_lookup

    async def __call__(self, cmd: CreateProductCommand) -> ProductDTO:
        slug = Slug(cmd.slug)
        requested_tags = list(dict.fromkeys(cmd.tag_slugs))  # dedupe, keep order
        images = await resolve_product_images(cmd.media_ids, self._media_lookup)

        async with self._uow_factory() as uow:
            if await uow.products.slug_exists(slug.value):
                raise SlugAlreadyTaken(slug.value)

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
                tags=tuple(tags),
                images=images,
            )
            await uow.products.add(product)
            await uow.commit()

        return ProductDTO.from_entity(product)
