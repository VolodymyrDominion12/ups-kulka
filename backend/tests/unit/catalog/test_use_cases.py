import pytest

from tests.fakes.catalog import FakeCatalogUnitOfWork
from ups_kulka.modules.catalog.application.dto import (
    CreateProductCommand,
    CreateTagCommand,
    ListProductsQuery,
)
from ups_kulka.modules.catalog.application.use_cases.create_product import CreateProduct
from ups_kulka.modules.catalog.application.use_cases.create_tag import CreateTag
from ups_kulka.modules.catalog.application.use_cases.get_product import GetProduct
from ups_kulka.modules.catalog.application.use_cases.list_products import ListProducts
from ups_kulka.modules.catalog.domain.errors import (
    InvalidTag,
    ProductNotFound,
    SlugAlreadyTaken,
    TagSlugAlreadyTaken,
    UnknownTags,
)
from ups_kulka.shared.application.pagination import InvalidPage


@pytest.fixture
def uow() -> FakeCatalogUnitOfWork:
    return FakeCatalogUnitOfWork()


async def _tag(uow: FakeCatalogUnitOfWork, slug: str, group: str = "recipient") -> None:
    await CreateTag(uow)(CreateTagCommand(group=group, slug=slug, name=slug))


def _cmd(slug: str = "rozhevyi-shyk", tags: tuple[str, ...] = ()) -> CreateProductCommand:
    return CreateProductCommand(
        slug=slug, name="Рожевий шик", description="", price_kopecks=141000, tag_slugs=tags
    )


async def test_create_product_with_tags(uow: FakeCatalogUnitOfWork) -> None:
    await _tag(uow, "dlia-divchynky")
    await _tag(uow, "pastelni", group="color")

    dto = await CreateProduct(uow)(_cmd(tags=("pastelni", "dlia-divchynky", "pastelni")))

    assert dto.slug == "rozhevyi-shyk"
    assert dto.price_kopecks == 141000
    assert {t.slug for t in dto.tags} == {"dlia-divchynky", "pastelni"}
    assert "rozhevyi-shyk" in uow.committed_products


async def test_create_product_duplicate_slug(uow: FakeCatalogUnitOfWork) -> None:
    await CreateProduct(uow)(_cmd())
    with pytest.raises(SlugAlreadyTaken):
        await CreateProduct(uow)(_cmd())


async def test_create_product_unknown_tags_not_saved(uow: FakeCatalogUnitOfWork) -> None:
    with pytest.raises(UnknownTags) as exc_info:
        await CreateProduct(uow)(_cmd(tags=("nema-takoho",)))
    assert exc_info.value.slugs == ["nema-takoho"]
    assert uow.committed_products == {}


async def test_get_product_hides_inactive(uow: FakeCatalogUnitOfWork) -> None:
    await CreateProduct(uow)(_cmd())
    uow.committed_products["rozhevyi-shyk"].deactivate()
    with pytest.raises(ProductNotFound):
        await GetProduct(uow)("rozhevyi-shyk")


async def test_get_product_not_found(uow: FakeCatalogUnitOfWork) -> None:
    with pytest.raises(ProductNotFound):
        await GetProduct(uow)("nema-takoho")


async def test_list_products_filters_by_tag_and_paginates(uow: FakeCatalogUnitOfWork) -> None:
    await _tag(uow, "dlia-divchynky")
    for i in range(5):
        await CreateProduct(uow)(_cmd(slug=f"girl-{i}", tags=("dlia-divchynky",)))
    await CreateProduct(uow)(_cmd(slug="untagged"))

    page = await ListProducts(uow)(ListProductsQuery(tag_slug="dlia-divchynky", limit=2))

    assert page.total == 5
    assert len(page.items) == 2
    assert all(any(t.slug == "dlia-divchynky" for t in p.tags) for p in page.items)


async def test_list_products_rejects_too_big_limit(uow: FakeCatalogUnitOfWork) -> None:
    with pytest.raises(InvalidPage):
        await ListProducts(uow)(ListProductsQuery(limit=101))


async def test_create_tag_rejects_unknown_group(uow: FakeCatalogUnitOfWork) -> None:
    with pytest.raises(InvalidTag):
        await CreateTag(uow)(CreateTagCommand(group="planet", slug="mars", name="Марс"))


async def test_create_tag_duplicate(uow: FakeCatalogUnitOfWork) -> None:
    await _tag(uow, "pastelni", group="color")
    with pytest.raises(TagSlugAlreadyTaken):
        await _tag(uow, "pastelni", group="color")
