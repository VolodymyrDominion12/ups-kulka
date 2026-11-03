import uuid
from datetime import date

import pytest

from tests.fakes.orders import (
    FakeOrdersUnitOfWork,
    FakePaymentStarter,
    FakeProductCatalog,
    RecordingOrderNotifier,
)
from ups_kulka.modules.orders.application.dto import (
    CatalogProduct,
    OrderLineInput,
    PlaceOrderCommand,
)
from ups_kulka.modules.orders.application.use_cases.get_checkout_options import (
    GetCheckoutOptions,
)
from ups_kulka.modules.orders.application.use_cases.place_order import PlaceOrder
from ups_kulka.modules.orders.domain.errors import (
    AddressRequired,
    InvalidOrder,
    OnlinePaymentUnavailable,
    ProductUnavailable,
)

HEART = CatalogProduct(id=uuid.uuid4(), name="Серце", price_kopecks=15500, is_active=True)
BOX = CatalogProduct(id=uuid.uuid4(), name="Коробка №1", price_kopecks=288500, is_active=True)
HIDDEN = CatalogProduct(id=uuid.uuid4(), name="Знято", price_kopecks=100, is_active=False)


def _use_case(
    *,
    uow: FakeOrdersUnitOfWork | None = None,
    payments: FakePaymentStarter | None = None,
    notifier: RecordingOrderNotifier | None = None,
) -> PlaceOrder:
    return PlaceOrder(
        uow_factory=uow or FakeOrdersUnitOfWork(),
        catalog=FakeProductCatalog(HEART, BOX, HIDDEN),
        payments=payments or FakePaymentStarter(),
        notifier=notifier or RecordingOrderNotifier(),
        today=lambda: date(2026, 11, 3),
    )


def _cmd(**overrides: object) -> PlaceOrderCommand:
    values: dict[str, object] = {
        "customer_name": "Олена",
        "phone": "093 111 22 33",
        "delivery_method": "pickup",
        "payment_method": "on_delivery",
        "lines": (OrderLineInput(HEART.id, 3), OrderLineInput(BOX.id, 1)),
    }
    values.update(overrides)
    return PlaceOrderCommand(**values)  # type: ignore[arg-type]


async def test_prices_come_from_the_catalogue() -> None:
    uow, notifier = FakeOrdersUnitOfWork(), RecordingOrderNotifier()

    placed = await _use_case(uow=uow, notifier=notifier)(_cmd())

    assert placed.total_kopecks == 15500 * 3 + 288500
    assert placed.number == 1001
    assert placed.payment_url is None
    assert uow.commits == 1
    assert len(notifier.sent) == 1


async def test_taxi_order_keeps_the_address() -> None:
    uow = FakeOrdersUnitOfWork()
    await _use_case(uow=uow)(_cmd(delivery_method="taxi", address="вул. Хрещатик, 1"))
    assert uow.orders.saved[0].delivery.address == "вул. Хрещатик, 1"


async def test_taxi_without_address_is_rejected() -> None:
    with pytest.raises(AddressRequired):
        await _use_case()(_cmd(delivery_method="taxi"))


async def test_courier_is_not_offered() -> None:
    with pytest.raises(InvalidOrder):
        await _use_case()(_cmd(delivery_method="courier"))


@pytest.mark.parametrize("product", [HIDDEN.id, uuid.uuid4()])
async def test_inactive_or_unknown_product_is_rejected(product: uuid.UUID) -> None:
    uow = FakeOrdersUnitOfWork()
    with pytest.raises(ProductUnavailable) as exc_info:
        await _use_case(uow=uow)(
            _cmd(lines=(OrderLineInput(HEART.id, 1), OrderLineInput(product, 1)))
        )
    assert exc_info.value.product_ids == [product]
    assert uow.orders.saved == []


async def test_online_payment_is_rejected_while_switched_off() -> None:
    uow = FakeOrdersUnitOfWork()
    with pytest.raises(OnlinePaymentUnavailable):
        await _use_case(uow=uow)(_cmd(payment_method="online"))
    assert uow.orders.saved == []


async def test_online_payment_returns_payment_page() -> None:
    payments = FakePaymentStarter(enabled=True)
    placed = await _use_case(payments=payments)(_cmd(payment_method="online"))
    assert placed.payment_url == "https://pay.example/1001"
    assert payments.started[0].number == 1001


async def test_bank_failure_keeps_the_order() -> None:
    uow = FakeOrdersUnitOfWork()
    placed = await _use_case(uow=uow, payments=FakePaymentStarter(enabled=True, fail=True))(
        _cmd(payment_method="online")
    )
    assert placed.payment_url is None
    assert uow.commits == 1


async def test_telegram_failure_keeps_the_order() -> None:
    uow = FakeOrdersUnitOfWork()
    placed = await _use_case(uow=uow, notifier=RecordingOrderNotifier(fail=True))(_cmd())
    assert placed.number == 1001
    assert uow.commits == 1


@pytest.mark.parametrize(
    ("enabled", "methods"), [(False, ("on_delivery",)), (True, ("on_delivery", "online"))]
)
async def test_checkout_options(enabled: bool, methods: tuple[str, ...]) -> None:
    options = await GetCheckoutOptions(FakePaymentStarter(enabled=enabled))()
    assert options.delivery_methods == ("pickup", "taxi")
    assert options.payment_methods == methods
