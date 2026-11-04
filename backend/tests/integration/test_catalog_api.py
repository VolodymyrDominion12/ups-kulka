import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration

API = "/api/v1/catalog"


async def _create_tag(client: AsyncClient, slug: str, group: str = "recipient") -> None:
    response = await client.post(f"{API}/tags", json={"group": group, "slug": slug, "name": slug})
    assert response.status_code == 201, response.text


async def _create_product(client: AsyncClient, slug: str, tags: list[str] | None = None) -> dict:
    response = await client.post(
        f"{API}/products",
        json={
            "slug": slug,
            "name": f"Набір {slug}",
            "price_kopecks": 99000,
            "tag_slugs": tags or [],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_and_get_product(client: AsyncClient) -> None:
    await _create_tag(client, "dlia-divchynky")
    created = await _create_product(client, "rozhevyi-shyk", ["dlia-divchynky"])

    response = await client.get(f"{API}/products/rozhevyi-shyk")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["price_kopecks"] == 99000
    assert [t["slug"] for t in body["tags"]] == ["dlia-divchynky"]


async def test_duplicate_slug_returns_409(client: AsyncClient) -> None:
    await _create_product(client, "rozhevyi-shyk")
    response = await client.post(
        f"{API}/products", json={"slug": "rozhevyi-shyk", "name": "X", "price_kopecks": 100}
    )
    assert response.status_code == 409
    assert response.json()["code"] == "slug_already_taken"


async def test_unknown_product_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"{API}/products/nema-takoho")
    assert response.status_code == 404
    assert response.json()["code"] == "product_not_found"


async def test_unknown_tag_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        f"{API}/products",
        json={"slug": "test-kulka", "name": "X", "price_kopecks": 100, "tag_slugs": ["nema"]},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "unknown_tags"


async def test_list_products_by_tag(client: AsyncClient) -> None:
    await _create_tag(client, "dlia-khlopchyka")
    await _create_product(client, "kosmos", ["dlia-khlopchyka"])
    await _create_product(client, "traktor", ["dlia-khlopchyka"])
    await _create_product(client, "sertse")

    response = await client.get(f"{API}/products", params={"tag": "dlia-khlopchyka"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [p["slug"] for p in body["items"]] == ["traktor", "kosmos"]  # newest first


async def test_list_limit_is_capped(client: AsyncClient) -> None:
    response = await client.get(f"{API}/products", params={"limit": 101})
    assert response.status_code == 422


async def test_get_tag_detail_with_seo_and_indexability(client: AsyncClient) -> None:
    await _create_tag(client, "vypyska", group="occasion")

    response = await client.get(f"{API}/tags/vypyska")

    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "vypyska"
    assert body["product_count"] == 0
    assert body["is_indexable"] is False  # no unique text yet
    assert body["faq"] == []
    assert body["seo_text"] == ""


async def test_unknown_tag_detail_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"{API}/tags/nema-takoho")
    assert response.status_code == 404
    assert response.json()["code"] == "tag_not_found"


async def test_list_tags_returns_active_product_counts(client: AsyncClient) -> None:
    await _create_tag(client, "vypyska", group="occasion")
    await _create_product(client, "prod-1", ["vypyska"])
    await _create_product(client, "prod-2", ["vypyska"])

    response = await client.get(f"{API}/tags")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["product_count"] == 2
    assert body[0]["is_indexable"] is False


async def test_list_products_search_by_name_and_slug(client: AsyncClient) -> None:
    await _create_product(client, "yedynorih")
    await _create_product(client, "sertse")

    response = await client.get(f"{API}/products", params={"q": "sertse"})

    assert response.status_code == 200
    assert [p["slug"] for p in response.json()["items"]] == ["sertse"]


async def test_list_products_sort_and_on_sale(client: AsyncClient) -> None:
    for slug, price, old in (("cheap", 10000, None), ("mid", 50000, None), ("sale", 90000, 120000)):
        resp = await client.post(
            f"{API}/products",
            json={"slug": slug, "name": slug, "price_kopecks": price, "old_price_kopecks": old},
        )
        assert resp.status_code == 201, resp.text

    asc = await client.get(f"{API}/products", params={"sort": "price_asc"})
    assert [p["price_kopecks"] for p in asc.json()["items"]] == [10000, 50000, 90000]

    on_sale = await client.get(f"{API}/products", params={"on_sale": "true"})
    assert [p["slug"] for p in on_sale.json()["items"]] == ["sale"]

    invalid = await client.get(f"{API}/products", params={"sort": "bogus"})
    assert invalid.status_code == 422


async def test_list_related_products_by_shared_tags(client: AsyncClient) -> None:
    await _create_tag(client, "pastelni", group="color")
    await _create_tag(client, "dlia-divchynky")
    await _create_product(client, "target", ["pastelni", "dlia-divchynky"])
    await _create_product(client, "one-tag", ["pastelni"])
    await _create_product(client, "unrelated")

    response = await client.get(f"{API}/products/target/related")

    assert response.status_code == 200
    assert [p["slug"] for p in response.json()] == ["one-tag"]

    unknown = await client.get(f"{API}/products/nema/related")
    assert unknown.status_code == 200
    assert unknown.json() == []
