import uuid

import pytest

from tests.fakes.catalog import FakeCatalogUnitOfWork
from ups_kulka.modules.catalog.application.dto import (
    CreateProductCommand,
    CreateTagCommand,
    FaqItemDTO,
    UpdateTagSeoCommand,
)
from ups_kulka.modules.catalog.application.use_cases.create_product import CreateProduct
from ups_kulka.modules.catalog.application.use_cases.create_tag import CreateTag
from ups_kulka.modules.catalog.application.use_cases.get_tag_detail import GetTagDetail
from ups_kulka.modules.catalog.application.use_cases.list_tags import ListTags
from ups_kulka.modules.catalog.application.use_cases.update_tag_seo import UpdateTagSeo
from ups_kulka.modules.catalog.domain.entities import (
    MIN_PRODUCTS_FOR_INDEXING,
    SEO_TITLE_MAX_LENGTH,
    FaqItem,
    Tag,
    TagGroup,
)
from ups_kulka.modules.catalog.domain.errors import InvalidTag, TagNotFound


@pytest.fixture
def uow() -> FakeCatalogUnitOfWork:
    return FakeCatalogUnitOfWork()


async def _tag(
    uow: FakeCatalogUnitOfWork,
    slug: str,
    name: str | None = None,
    group: str = "occasion",
) -> None:
    await CreateTag(uow)(CreateTagCommand(group=group, slug=slug, name=name or slug))


async def _product(uow: FakeCatalogUnitOfWork, slug: str, tag_slug: str) -> None:
    await CreateProduct(uow)(
        CreateProductCommand(
            slug=slug, name=slug, description="", price_kopecks=10000, tag_slugs=(tag_slug,)
        )
    )


def _base_tag() -> Tag:
    return Tag.create(group=TagGroup.OCCASION, slug="vypyska", name="Виписка")


# --- domain ---


def test_tag_is_indexable_requires_unique_text_and_min_products() -> None:
    tag = _base_tag()
    assert tag.has_unique_text is False
    assert tag.is_indexable(10) is False

    tag = tag.with_seo(seo_text="Унікальний текст про виписку")
    assert tag.has_unique_text is True
    assert tag.is_indexable(MIN_PRODUCTS_FOR_INDEXING - 1) is False
    assert tag.is_indexable(MIN_PRODUCTS_FOR_INDEXING) is True


def test_tag_with_seo_validates_lengths_and_faq() -> None:
    tag = _base_tag()
    with pytest.raises(InvalidTag):
        tag.with_seo(seo_title="x" * (SEO_TITLE_MAX_LENGTH + 1))
    with pytest.raises(InvalidTag):
        tag.with_seo(faq=(FaqItem(question="", answer="a"),))
    with pytest.raises(InvalidTag):
        tag.with_seo(faq=(FaqItem(question="q", answer=""),))


def test_tag_with_seo_strips_and_is_immutable() -> None:
    tag = _base_tag()
    updated = tag.with_seo(seo_title="  Кульки  ", faq=(FaqItem(question=" q ", answer=" a "),))
    assert updated.seo_title == "Кульки"
    assert updated.faq[0].question == "q"
    assert tag.seo_title == ""


# --- use cases ---


async def test_get_tag_detail_and_update_seo(uow: FakeCatalogUnitOfWork) -> None:
    await _tag(uow, "vypyska", "Виписка")
    detail = await GetTagDetail(uow)("vypyska")
    assert detail.slug == "vypyska"
    assert detail.product_count == 0
    assert detail.is_indexable is False

    updated = await UpdateTagSeo(uow)(
        UpdateTagSeoCommand(
            tag_id=detail.id,
            seo_title="Гелієві кульки на виписку — Київ",
            seo_text="Унікальний текст",
            faq=(FaqItemDTO(question="Скільки тримається?", answer="3–5 днів"),),
        )
    )
    assert updated.seo_title == "Гелієві кульки на виписку — Київ"
    assert updated.faq[0].question == "Скільки тримається?"

    again = await GetTagDetail(uow)("vypyska")
    assert again.seo_title == "Гелієві кульки на виписку — Київ"
    assert again.faq[0].answer == "3–5 днів"


async def test_get_tag_detail_not_found(uow: FakeCatalogUnitOfWork) -> None:
    with pytest.raises(TagNotFound):
        await GetTagDetail(uow)("nema")


async def test_update_tag_seo_not_found(uow: FakeCatalogUnitOfWork) -> None:
    with pytest.raises(TagNotFound):
        await UpdateTagSeo(uow)(UpdateTagSeoCommand(tag_id=uuid.uuid4(), seo_text="x"))


async def test_list_tags_returns_counts_and_indexability(uow: FakeCatalogUnitOfWork) -> None:
    await _tag(uow, "vypyska", "Виписка")
    await _tag(uow, "pastelni", "Пастельні", group="color")
    for i in range(MIN_PRODUCTS_FOR_INDEXING):
        await _product(uow, f"vp-{i}", "vypyska")

    detail = await GetTagDetail(uow)("vypyska")
    await UpdateTagSeo(uow)(UpdateTagSeoCommand(tag_id=detail.id, seo_text="Унікальний текст"))

    summaries = await ListTags(uow)()
    by_slug = {s.slug: s for s in summaries}
    assert by_slug["vypyska"].product_count == MIN_PRODUCTS_FOR_INDEXING
    assert by_slug["vypyska"].is_indexable is True
    assert by_slug["pastelni"].product_count == 0
    assert by_slug["pastelni"].is_indexable is False
