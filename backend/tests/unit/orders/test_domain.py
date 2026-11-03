import uuid
from datetime import date

import pytest

from ups_kulka.modules.orders.domain.entities import (
    Customer,
    Delivery,
    DeliveryMethod,
    Order,
    OrderItem,
    PaymentMethod,
    PhoneNumber,
)
from ups_kulka.modules.orders.domain.errors import (
    AddressRequired,
    DeliveryDateInPast,
    InvalidOrder,
    InvalidPhone,
)
from ups_kulka.shared.domain.money import Money

TODAY = date(2026, 11, 3)


@pytest.mark.parametrize(
    "raw", ["093 111 22 33", "0931112233", "+380931112233", "38 (093) 111-22-33"]
)
def test_phone_is_normalized(raw: str) -> None:
    assert PhoneNumber.parse(raw).value == "+380931112233"


@pytest.mark.parametrize("raw", ["12345", "+44 20 7946 0958", "", "093111223"])
def test_bad_phone_is_rejected(raw: str) -> None:
    with pytest.raises(InvalidPhone):
        PhoneNumber.parse(raw)


def test_customer_needs_a_name() -> None:
    with pytest.raises(InvalidOrder):
        Customer.create(name="  ", phone="0931112233")


def test_taxi_needs_an_address() -> None:
    with pytest.raises(AddressRequired):
        Delivery.create(method=DeliveryMethod.TAXI, today=TODAY, address="   ")


def test_pickup_ignores_address_and_cleans_slot() -> None:
    delivery = Delivery.create(
        method=DeliveryMethod.PICKUP, today=TODAY, address="вул. Хрещатик, 1", time_slot=" "
    )
    assert delivery.address is None
    assert delivery.time_slot is None


def test_delivery_date_cannot_be_in_the_past() -> None:
    with pytest.raises(DeliveryDateInPast):
        Delivery.create(method=DeliveryMethod.PICKUP, today=TODAY, on_date=date(2026, 11, 2))


def _item(product_id: uuid.UUID, quantity: int, price: int = 15500) -> OrderItem:
    return OrderItem(product_id, "Серце", Money(price), quantity)


def _place(items: list[OrderItem]) -> Order:
    return Order.place(
        customer=Customer.create(name="Олена", phone="0931112233"),
        delivery=Delivery.create(method=DeliveryMethod.PICKUP, today=TODAY),
        items=items,
        payment_method=PaymentMethod.ON_DELIVERY,
    )


def test_same_products_are_merged_and_total_is_computed() -> None:
    heart, box = uuid.uuid4(), uuid.uuid4()
    order = _place([_item(heart, 2), _item(box, 1, price=200000), _item(heart, 1)])

    assert [(i.product_id, i.quantity) for i in order.items] == [(heart, 3), (box, 1)]
    assert order.total == Money(15500 * 3 + 200000)


def test_merged_quantity_is_still_limited() -> None:
    heart = uuid.uuid4()
    with pytest.raises(InvalidOrder):
        _place([_item(heart, 60), _item(heart, 60)])


def test_empty_order_is_rejected() -> None:
    with pytest.raises(InvalidOrder):
        _place([])


def test_too_many_different_products() -> None:
    with pytest.raises(InvalidOrder):
        _place([_item(uuid.uuid4(), 1) for _ in range(51)])


def test_number_is_assigned_once() -> None:
    order = _place([_item(uuid.uuid4(), 1)])
    order.assign_number(1001)
    with pytest.raises(InvalidOrder):
        order.assign_number(1002)
