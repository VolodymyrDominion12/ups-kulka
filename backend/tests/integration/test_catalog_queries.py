"""N+1 guard: query count must not grow with the number of rows (AGENTS.md, section 5)."""

import pytest

from tests.conftest import QueryCounter
from ups_kulka.container import Container
from ups_kulka.modules.catalog.application.dto import (
    CreateProductCommand,
    CreateTagCommand,
    ListProductsQuery,
)

pytestmark = pytest.mark.integration

LIST_QUERIES = 4  # count + page + selectinload(tags) + selectinload(media)
GET_QUERIES = 3  # product + selectinload(tags) + selectinload(media)


async def _seed(container: Container, products: int, tags_per_product: int) -> None:
    create_tag = container.catalog.create_tag()
    create_product = container.catalog.create_product()
    tag_slugs = [f"tag-{i}" for i in range(tags_per_product)]
    for slug in tag_slugs:
        await create_tag(CreateTagCommand(group="theme", slug=slug, name=slug))
    for i in range(products):
        await create_product(
            CreateProductCommand(
                slug=f"product-{i}",
                name=f"Product {i}",
                description="",
                price_kopecks=10000,
                tag_slugs=tuple(tag_slugs),
            )
        )


@pytest.mark.parametrize(("products", "tags"), [(1, 1), (30, 5)])
async def test_list_products_query_count_is_constant(
    container: Container, query_counter: QueryCounter, products: int, tags: int
) -> None:
    await _seed(container, products, tags)
    list_products = container.catalog.list_products()

    with query_counter.assert_max_queries(LIST_QUERIES):
        page = await list_products(ListProductsQuery(limit=50))

    assert len(page.items) == products
    assert all(len(item.tags) == tags for item in page.items)


@pytest.mark.parametrize(("products", "tags"), [(1, 1), (30, 5)])
async def test_list_by_tag_query_count_is_constant(
    container: Container, query_counter: QueryCounter, products: int, tags: int
) -> None:
    await _seed(container, products, tags)
    list_products = container.catalog.list_products()

    with query_counter.assert_max_queries(LIST_QUERIES):
        page = await list_products(ListProductsQuery(tag_slug="tag-0", limit=50))

    assert page.total == products


async def test_get_product_query_count(container: Container, query_counter: QueryCounter) -> None:
    await _seed(container, products=1, tags_per_product=10)
    get_product = container.catalog.get_product()

    with query_counter.assert_max_queries(GET_QUERIES):
        product = await get_product("product-0")

    assert len(product.tags) == 10


async def test_create_product_links_tags_in_one_batch(
    container: Container, query_counter: QueryCounter
) -> None:
    await _seed(container, products=0, tags_per_product=20)
    create_product = container.catalog.create_product()
    command = CreateProductCommand(
        slug="many-tags",
        name="Many tags",
        description="",
        price_kopecks=100,
        tag_slugs=tuple(f"tag-{i}" for i in range(20)),
    )
    # exists check + tags lookup + insert product + batch insert links (+ BEGIN/COMMIT noise)
    with query_counter.assert_max_queries(6):
        await create_product(command)


async def test_list_tags_with_counts_is_one_query(
    container: Container, query_counter: QueryCounter
) -> None:
    create_tag = container.catalog.create_tag()
    for i in range(15):
        await create_tag(CreateTagCommand(group="theme", slug=f"t-{i}", name=f"t-{i}"))
    list_tags = container.catalog.list_tags()

    with query_counter.assert_max_queries(1):
        summaries = await list_tags()

    assert len(summaries) == 15
    assert all(s.product_count == 0 for s in summaries)


async def test_list_related_query_count_is_constant(
    container: Container, query_counter: QueryCounter
) -> None:
    create_tag = container.catalog.create_tag()
    create_product = container.catalog.create_product()
    for slug in ("a", "b", "c", "d", "e"):
        await create_tag(CreateTagCommand(group="theme", slug=f"tag-{slug}", name=slug))
    await create_product(
        CreateProductCommand(
            slug="target",
            name="Target",
            description="",
            price_kopecks=100,
            tag_slugs=("tag-a", "tag-b"),
        )
    )
    for i in range(12):
        await create_product(
            CreateProductCommand(
                slug=f"rel-{i}",
                name=f"Rel {i}",
                description="",
                price_kopecks=100,
                tag_slugs=("tag-a",),
            )
        )

    list_related = container.catalog.list_related_products()

    # ids (GROUP BY) + products + selectinload(tags) + selectinload(media)
    with query_counter.assert_max_queries(4):
        related = await list_related("target")

    assert len(related) == 8  # RELATED_PRODUCTS_LIMIT
