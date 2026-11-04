"""Integration tests for admin auth, media pipeline, salon quick product creation,
admin orders, and marketing analytics (specs/007, specs/009, specs/011)."""

import io
from pathlib import Path

import pytest
from dependency_injector import providers
from httpx import AsyncClient
from PIL import Image

from tests.conftest import QueryCounter
from tests.fakes.orders import RecordingSender
from ups_kulka.container import Container
from ups_kulka.modules.media.infrastructure.imaging import LocalFileMediaStorage

pytestmark = pytest.mark.integration


def _sample_jpeg() -> bytes:
    img = Image.new("RGB", (600, 750), color=(230, 179, 179))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


async def _login_headers(client: AsyncClient) -> dict[str, str]:
    resp = await client.post("/api/v1/admin/auth/login", json={"password": "admin123"})
    assert resp.status_code == 200, resp.text
    token = resp.json()["token"]
    return {"Authorization": f"Bearer {token}"}


async def test_admin_auth_required_on_admin_endpoints(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/admin/orders")
    assert resp.status_code == 401
    assert resp.json()["code"] == "unauthorized"

    bad_login = await client.post("/api/v1/admin/auth/login", json={"password": "wrong"})
    assert bad_login.status_code == 401
    assert bad_login.json()["code"] == "invalid_admin_credentials"

    headers = await _login_headers(client)
    me = await client.get("/api/v1/admin/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["role"] == "admin"


async def test_salon_express_flow_media_and_catalog(
    client: AsyncClient,
    container: Container,
    query_counter: QueryCounter,
    tmp_path: Path,
) -> None:
    container.media.storage.override(providers.Object(LocalFileMediaStorage(str(tmp_path))))
    headers = await _login_headers(client)

    # 1. Create tags
    await client.post(
        "/api/v1/catalog/tags",
        json={"group": "occasion", "slug": "den-narodzhennia", "name": "День народження"},
    )
    await client.post(
        "/api/v1/catalog/tags",
        json={"group": "recipient", "slug": "dlia-divchynky", "name": "Для дівчинки"},
    )
    tags_resp = await client.get("/api/v1/catalog/tags")
    assert tags_resp.status_code == 200
    assert len(tags_resp.json()) == 2

    # 2. Upload photo from smartphone camera
    upload_resp = await client.post(
        "/api/v1/admin/media",
        headers=headers,
        files={"file": ("camera_photo.jpg", _sample_jpeg(), "image/jpeg")},
    )
    assert upload_resp.status_code == 201, upload_resp.text
    media_data = upload_resp.json()
    media_id = media_data["id"]
    assert media_data["width"] == 600
    assert media_data["height"] == 750
    assert "640w" in media_data["variants"]

    # 3. Express publish product without manual slug
    quick_resp = await client.post(
        "/api/v1/admin/catalog/products",
        headers=headers,
        json={
            "name": "Рожевий фонтан з кулькою",
            "price_kopecks": 145000,
            "old_price_kopecks": 170000,
            "description": "Свіжа композиція прямо з салону",
            "tag_slugs": ["den-narodzhennia", "dlia-divchynky"],
            "media_ids": [media_id],
        },
    )
    assert quick_resp.status_code == 201, quick_resp.text
    prod1 = quick_resp.json()
    assert prod1["slug"] == "rozhevyi-fontan-z-kulkoiu"
    assert prod1["old_price_kopecks"] == 170000
    assert len(prod1["images"]) == 1
    assert prod1["images"][0]["media_id"] == media_id

    # 4. Duplicate Ukrainian name gets "-2" automatically
    quick_resp2 = await client.post(
        "/api/v1/admin/catalog/products",
        headers=headers,
        json={
            "name": "Рожевий фонтан з кулькою",
            "price_kopecks": 150000,
            "tag_slugs": ["dlia-divchynky"],
            "media_ids": [media_id],
        },
    )
    assert quick_resp2.status_code == 201
    assert quick_resp2.json()["slug"] == "rozhevyi-fontan-z-kulkoiu-2"

    # 5. Update product via PATCH
    patch_resp = await client.patch(
        f"/api/v1/admin/catalog/products/{prod1['id']}",
        headers=headers,
        json={"price_kopecks": 139000, "is_active": False},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["price_kopecks"] == 139000
    assert patch_resp.json()["is_active"] is False

    # 6. Admin list shows both active and inactive with constant queries (no N+1)
    with query_counter.assert_max_queries(5):
        admin_list = await client.get("/api/v1/admin/catalog/products", headers=headers)
    assert admin_list.status_code == 200
    assert admin_list.json()["total"] == 2


async def test_admin_orders_and_analytics_api_no_n_plus_one(
    client: AsyncClient,
    container: Container,
    query_counter: QueryCounter,
) -> None:
    container.notifications.sender.override(providers.Object(RecordingSender()))
    headers = await _login_headers(client)

    await client.post(
        "/api/v1/catalog/tags",
        json={"group": "occasion", "slug": "vypyska", "name": "Виписка"},
    )
    prod_resp = await client.post(
        "/api/v1/admin/catalog/products",
        headers=headers,
        json={
            "name": "Набір на виписку Хмаринка",
            "price_kopecks": 180000,
            "tag_slugs": ["vypyska"],
        },
    )
    prod_id = prod_resp.json()["id"]

    # Place storefront order with UTM attribution
    order_resp = await client.post(
        "/api/v1/orders",
        json={
            "customer": {"name": "Ірина", "phone": "093 555 66 77"},
            "delivery": {
                "method": "taxi",
                "address": "просп. Червоної Калини, 45",
                "date": "2026-11-05",
                "time_slot": "10:00-12:00",
            },
            "payment_method": "on_delivery",
            "items": [{"product_id": prod_id, "quantity": 1}],
            "marketing": {
                "utm_source": "instagram",
                "utm_medium": "stories",
                "utm_campaign": "autumn_vypyska",
                "landing_page": "/kulky/vypyska",
                "promo_code": "MAMA5",
            },
        },
    )
    assert order_resp.status_code == 201, order_resp.text
    order_num = order_resp.json()["number"]

    # Create a walk-in salon order from admin
    admin_order_resp = await client.post(
        "/api/v1/admin/orders",
        headers=headers,
        json={
            "customer": {"name": "Ірина", "phone": "093 555 66 77"},
            "delivery": {"method": "pickup"},
            "payment_method": "on_delivery",
            "order_source": "walk_in",
            "discount_kopecks": 10000,
            "internal_note": "Забере сама о 17:00",
            "items": [{"product_id": prod_id, "quantity": 2}],
        },
    )
    assert admin_order_resp.status_code == 201, admin_order_resp.text

    # Update status of first order
    upd = await client.patch(
        f"/api/v1/admin/orders/{order_num}",
        headers=headers,
        json={"status": "confirmed", "status_note": "Підтверджено у Viber"},
    )
    assert upd.status_code == 200
    assert upd.json()["status"] == "confirmed"
    assert len(upd.json()["status_history"]) == 2

    # Check admin orders list query count (no N+1)
    with query_counter.assert_max_queries(5):
        orders_list = await client.get("/api/v1/admin/orders", headers=headers)
    assert orders_list.status_code == 200
    assert orders_list.json()["total"] == 2

    # Check analytics dashboard query count (no N+1)
    with query_counter.assert_max_queries(7):
        dash = await client.get("/api/v1/admin/analytics/dashboard", headers=headers)
    assert dash.status_code == 200
    dash_data = dash.json()
    assert dash_data["kpi"]["orders_count"] == 2
    assert dash_data["kpi"]["revenue_kopecks"] == 180000 + 350000
    assert dash_data["kpi"]["repeat_customers_count"] == 1
    assert any(b["key"] == "instagram" for b in dash_data["by_utm_source"])
    assert any(t["tag_slug"] == "vypyska" for t in dash_data["by_tag_group"])

    # Check CRM customers endpoint
    crm = await client.get("/api/v1/admin/analytics/customers", headers=headers)
    assert crm.status_code == 200
    assert crm.json()["total"] == 1
    assert crm.json()["items"][0]["orders_count"] == 2

    # Check anniversaries endpoint
    anniv = await client.get("/api/v1/admin/analytics/anniversaries", headers=headers)
    assert anniv.status_code == 200


async def test_admin_update_tag_seo(client: AsyncClient) -> None:
    headers = await _login_headers(client)
    tag_resp = await client.post(
        "/api/v1/catalog/tags",
        json={"group": "occasion", "slug": "vypyska", "name": "Виписка"},
    )
    assert tag_resp.status_code == 201, tag_resp.text
    tag_id = tag_resp.json()["id"]

    unauth = await client.patch(f"/api/v1/admin/catalog/tags/{tag_id}", json={"seo_text": "Текст"})
    assert unauth.status_code == 401

    resp = await client.patch(
        f"/api/v1/admin/catalog/tags/{tag_id}",
        headers=headers,
        json={
            "seo_title": "Гелієві кульки на виписку — Київ",
            "seo_text": "Унікальний текст підбірки",
            "faq": [{"question": "Скільки тримається гелій?", "answer": "3–5 днів"}],
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["seo_title"] == "Гелієві кульки на виписку — Київ"
    assert body["is_indexable"] is False  # no active products yet

    detail = await client.get("/api/v1/catalog/tags/vypyska")
    assert detail.status_code == 200
    assert detail.json()["faq"][0]["question"] == "Скільки тримається гелій?"
