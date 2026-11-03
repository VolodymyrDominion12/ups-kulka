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
        json={"slug": slug, "name": f"Набір {slug}", "price_kopecks": 99000, "tag_slugs": tags or []},
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
