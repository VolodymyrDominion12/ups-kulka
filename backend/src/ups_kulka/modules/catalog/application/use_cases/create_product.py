from ups_kulka.modules.catalog.application.dto import CreateProductCommand, ProductDTO
from ups_kulka.modules.catalog.application.ports import CatalogUnitOfWorkFactory
from ups_kulka.modules.catalog.domain.entities import Product, Slug
from ups_kulka.modules.catalog.domain.errors import SlugAlreadyTaken, UnknownTags
from ups_kulka.shared.domain.money import Money


class CreateProduct:
    def __init__(self, uow_factory: CatalogUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self, cmd: CreateProductCommand) -> ProductDTO:
        slug = Slug(cmd.slug)
        requested_tags = list(dict.fromkeys(cmd.tag_slugs))  # dedupe, keep order

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
                tags=tuple(tags),
            )
            await uow.products.add(product)
            await uow.commit()

        return ProductDTO.from_entity(product)
