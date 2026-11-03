import datetime as dt
import re
import uuid
from dataclasses import dataclass
from enum import StrEnum

from ups_kulka.modules.orders.domain.errors import (
    AddressRequired,
    DeliveryDateInPast,
    InvalidOrder,
    InvalidPhone,
)
from ups_kulka.shared.domain.money import Money

MAX_LINES = 50
MAX_QUANTITY = 99
_NON_DIGITS = re.compile(r"\D")


@dataclass(frozen=True, slots=True)
class PhoneNumber:
    """Ukrainian mobile/landline number stored as +380XXXXXXXXX."""

    value: str

    @classmethod
    def parse(cls, raw: str) -> "PhoneNumber":
        digits = _NON_DIGITS.sub("", raw)
        if len(digits) == 10 and digits.startswith("0"):
            digits = "38" + digits
        if len(digits) != 12 or not digits.startswith("380"):
            raise InvalidPhone
        return cls("+" + digits)


@dataclass(frozen=True, slots=True)
class Customer:
    name: str
    phone: PhoneNumber
    comment: str = ""

    @classmethod
    def create(cls, *, name: str, phone: str, comment: str = "") -> "Customer":
        clean_name = name.strip()
        if not clean_name:
            raise InvalidOrder("Вкажіть імʼя")
        return cls(name=clean_name, phone=PhoneNumber.parse(phone), comment=comment.strip())


class DeliveryMethod(StrEnum):
    PICKUP = "pickup"
    # No own couriers: the shop sends a taxi, the customer pays the fare separately.
    TAXI = "taxi"


class PaymentMethod(StrEnum):
    ON_DELIVERY = "on_delivery"
    ONLINE = "online"


class OrderStatus(StrEnum):
    NEW = "new"


@dataclass(frozen=True, slots=True)
class Delivery:
    method: DeliveryMethod
    address: str | None = None
    date: dt.date | None = None
    time_slot: str | None = None

    @classmethod
    def create(
        cls,
        *,
        method: DeliveryMethod,
        today: dt.date,
        address: str | None = None,
        on_date: dt.date | None = None,
        time_slot: str | None = None,
    ) -> "Delivery":
        clean_address = (address or "").strip() or None
        if method is DeliveryMethod.TAXI and clean_address is None:
            raise AddressRequired
        if on_date is not None and on_date < today:
            raise DeliveryDateInPast
        return cls(
            method=method,
            address=clean_address if method is DeliveryMethod.TAXI else None,
            date=on_date,
            time_slot=(time_slot or "").strip() or None,
        )


@dataclass(frozen=True, slots=True)
class OrderItem:
    """Name and price are a snapshot from the catalogue at the moment of the order."""

    product_id: uuid.UUID
    product_name: str
    unit_price: Money
    quantity: int

    def __post_init__(self) -> None:
        if not 1 <= self.quantity <= MAX_QUANTITY:
            raise InvalidOrder(f"Кількість одного товару — від 1 до {MAX_QUANTITY}")

    @property
    def total(self) -> Money:
        return self.unit_price * self.quantity


@dataclass(slots=True)
class Order:
    id: uuid.UUID
    customer: Customer
    delivery: Delivery
    items: tuple[OrderItem, ...]
    payment_method: PaymentMethod
    status: OrderStatus
    created_at: dt.datetime
    number: int | None = None

    @classmethod
    def place(
        cls,
        *,
        customer: Customer,
        delivery: Delivery,
        items: list[OrderItem],
        payment_method: PaymentMethod,
    ) -> "Order":
        merged: dict[uuid.UUID, OrderItem] = {}
        for item in items:
            previous = merged.get(item.product_id)
            quantity = item.quantity + (previous.quantity if previous else 0)
            merged[item.product_id] = OrderItem(
                product_id=item.product_id,
                product_name=item.product_name,
                unit_price=item.unit_price,
                quantity=quantity,
            )
        if not merged:
            raise InvalidOrder("Кошик порожній")
        if len(merged) > MAX_LINES:
            raise InvalidOrder(f"В одному замовленні — до {MAX_LINES} різних товарів")
        return cls(
            id=uuid.uuid4(),
            customer=customer,
            delivery=delivery,
            items=tuple(merged.values()),
            payment_method=payment_method,
            status=OrderStatus.NEW,
            created_at=dt.datetime.now(dt.UTC),
        )

    def assign_number(self, number: int) -> None:
        if self.number is not None:
            raise InvalidOrder("Order number is already assigned")
        self.number = number

    @property
    def total(self) -> Money:
        total = Money(0)
        for item in self.items:
            total = total + item.total
        return total
