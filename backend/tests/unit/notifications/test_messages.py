from datetime import date

from tests.fakes.orders import RecordingSender
from ups_kulka.modules.notifications.application.dto import (
    NoticeLine,
    OrderPlacedNotice,
    PaymentReceivedNotice,
)
from ups_kulka.modules.notifications.application.messages import format_uah
from ups_kulka.modules.notifications.application.public import NotificationsFacade
from ups_kulka.modules.notifications.application.use_cases.notify_shop import (
    NotifyOrderPlaced,
    NotifyPaymentReceived,
)


def _notice(**overrides: object) -> OrderPlacedNotice:
    values: dict[str, object] = {
        "number": 1001,
        "lines": (NoticeLine(name="Серце", quantity=3, total_kopecks=46500),),
        "total_kopecks": 46500,
        "customer_name": "Олена",
        "customer_phone": "+380931112233",
        "delivery_method": "taxi",
        "payment_method": "on_delivery",
        "address": "вул. Хрещатик, 1",
        "delivery_date": date(2026, 11, 5),
        "time_slot": "14–16",
        "comment": "Напис «Соня»",
    }
    values.update(overrides)
    return OrderPlacedNotice(**values)  # type: ignore[arg-type]


def _facade(sender: RecordingSender) -> NotificationsFacade:
    return NotificationsFacade(NotifyOrderPlaced(sender), NotifyPaymentReceived(sender))


def test_format_uah() -> None:
    assert format_uah(288500) == "2 885 грн"
    assert format_uah(15550) == "155,50 грн"


async def test_taxi_order_text_tells_who_pays_the_fare() -> None:
    sender = RecordingSender()
    await _facade(sender).order_placed(_notice())
    text = sender.texts[0]
    assert "№1001" in text
    assert "Серце × 3 = 465 грн" in text
    assert "Таксі на адресу: вул. Хрещатик, 1" in text
    assert "Поїздку оплачує клієнт" in text
    assert "05.11.2026 14–16" in text
    assert "Оплата при отриманні" in text


async def test_pickup_online_order_text() -> None:
    sender = RecordingSender()
    await _facade(sender).order_placed(
        _notice(delivery_method="pickup", address=None, payment_method="online",
                payment_url="https://pay.example/x", comment="")
    )  # fmt: skip
    text = sender.texts[0]
    assert "Самовивіз" in text
    assert "Онлайн-оплата: очікуємо" in text
    assert "💬" not in text


async def test_payment_received_text() -> None:
    sender = RecordingSender()
    await _facade(sender).payment_received(
        PaymentReceivedNotice(order_number=1001, amount_kopecks=95000)
    )
    assert sender.texts == ["✅ Замовлення №1001 оплачено онлайн: 950 грн"]
