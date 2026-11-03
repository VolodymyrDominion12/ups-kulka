import pytest
from dependency_injector import providers
from httpx import AsyncClient

from tests.fakes.orders import FakePaymentGateway, RecordingSender
from ups_kulka.container import Container

pytestmark = pytest.mark.integration

CATALOG = "/api/v1/catalog"
ORDERS = "/api/v1/orders"


async def _product(client: AsyncClient, slug: str, price: int) -> str:
    response = await client.post(
        f"{CATALOG}/products", json={"slug": slug, "name": f"Кулька {slug}", "price_kopecks": price}
    )
    assert response.status_code == 201, response.text
    product_id: str = response.json()["id"]
    return product_id


def _order(*items: tuple[str, int], **overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "customer": {"name": "Олена", "phone": "093 111 22 33", "comment": "Напис «Соня»"},
        "delivery": {"method": "pickup"},
        "items": [{"product_id": pid, "quantity": qty} for pid, qty in items],
    }
    body.update(overrides)
    return body


@pytest.fixture
def sender(container: Container) -> RecordingSender:
    sender = RecordingSender()
    container.notifications.sender.override(providers.Object(sender))
    return sender


async def test_checkout_options_without_payment_keys(client: AsyncClient) -> None:
    response = await client.get(f"{ORDERS}/checkout-options")
    assert response.json() == {
        "delivery_methods": ["pickup", "taxi"],
        "payment_methods": ["on_delivery"],
    }


async def test_place_order_uses_catalogue_prices_and_notifies(
    client: AsyncClient, sender: RecordingSender
) -> None:
    heart = await _product(client, "sertse", 15500)
    box = await _product(client, "korobka-1", 288500)

    response = await client.post(f"{ORDERS}", json=_order((heart, 2), (box, 1), (heart, 1)))

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["number"] >= 1001
    assert body["total_kopecks"] == 15500 * 3 + 288500
    assert [(i["product_id"], i["quantity"]) for i in body["items"]] == [(heart, 3), (box, 1)]
    assert body["payment_url"] is None
    assert len(sender.texts) == 1
    assert f"№{body['number']}" in sender.texts[0]


async def test_order_numbers_grow(client: AsyncClient, sender: RecordingSender) -> None:
    heart = await _product(client, "sertse", 15500)
    first = (await client.post(f"{ORDERS}", json=_order((heart, 1)))).json()["number"]
    second = (await client.post(f"{ORDERS}", json=_order((heart, 1)))).json()["number"]
    assert second == first + 1


async def test_taxi_without_address(client: AsyncClient, sender: RecordingSender) -> None:
    heart = await _product(client, "sertse", 15500)
    response = await client.post(f"{ORDERS}", json=_order((heart, 1), delivery={"method": "taxi"}))
    assert response.status_code == 422
    assert response.json()["code"] == "address_required"


async def test_courier_is_not_accepted(client: AsyncClient, sender: RecordingSender) -> None:
    heart = await _product(client, "sertse", 15500)
    response = await client.post(
        f"{ORDERS}", json=_order((heart, 1), delivery={"method": "courier", "address": "x"})
    )
    assert response.status_code == 422


async def test_unknown_product(client: AsyncClient, sender: RecordingSender) -> None:
    response = await client.post(
        f"{ORDERS}", json=_order(("6f1c7e5e-0000-4000-8000-000000000000", 1))
    )
    assert response.status_code == 422
    assert response.json()["code"] == "product_unavailable"
    assert sender.texts == []


async def test_invalid_phone(client: AsyncClient, sender: RecordingSender) -> None:
    heart = await _product(client, "sertse", 15500)
    body = _order((heart, 1), customer={"name": "Оля", "phone": "1234567890"})
    response = await client.post(f"{ORDERS}", json=body)
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_phone"


async def test_online_payment_is_off_without_keys(
    client: AsyncClient, sender: RecordingSender
) -> None:
    heart = await _product(client, "sertse", 15500)
    response = await client.post(f"{ORDERS}", json=_order((heart, 1), payment_method="online"))
    assert response.status_code == 422
    assert response.json()["code"] == "online_payment_unavailable"


async def test_online_payment_and_webhook(
    container: Container, client: AsyncClient, sender: RecordingSender
) -> None:
    gateway = FakePaymentGateway()
    container.payments.gateway.override(providers.Object(gateway))
    heart = await _product(client, "sertse", 15500)

    placed = await client.post(f"{ORDERS}", json=_order((heart, 2), payment_method="online"))
    assert placed.status_code == 201, placed.text
    number = placed.json()["number"]
    assert placed.json()["payment_url"] == "https://pay.example/x"

    for _ in range(2):  # the bank may repeat webhooks
        hook = await client.post(
            "/api/v1/payments/monobank/webhook",
            json={"invoiceId": f"inv-{number}", "status": "failure"},  # body status is ignored
        )
        assert hook.status_code == 200, hook.text

    paid_messages = [t for t in sender.texts if "оплачено онлайн" in t]
    assert paid_messages == [f"✅ Замовлення №{number} оплачено онлайн: 310 грн"]


async def test_webhook_is_404_without_keys(client: AsyncClient) -> None:
    response = await client.post("/api/v1/payments/monobank/webhook", json={"invoiceId": "x"})
    assert response.status_code == 404
    assert response.json()["code"] == "payments_disabled"


async def test_webhook_unknown_invoice(container: Container, client: AsyncClient) -> None:
    container.payments.gateway.override(providers.Object(FakePaymentGateway()))
    response = await client.post("/api/v1/payments/monobank/webhook", json={"invoiceId": "nope"})
    assert response.status_code == 404
    assert response.json()["code"] == "payment_not_found"
