import datetime as dt
import re
import uuid
from dataclasses import dataclass, field
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
    CONFIRMED = "confirmed"
    ASSEMBLED = "assembled"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderSource(StrEnum):
    STOREFRONT = "storefront"
    INSTAGRAM = "instagram"
    TELEGRAM = "telegram"
    PHONE = "phone"
    WALK_IN = "walk_in"


@dataclass(frozen=True, slots=True)
class MarketingAttribution:
    order_source: OrderSource = OrderSource.STOREFRONT
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    landing_page: str | None = None
    promo_code: str | None = None
    discount_kopecks: int = 0

    @classmethod
    def create(
        cls,
        *,
        order_source: OrderSource = OrderSource.STOREFRONT,
        utm_source: str | None = None,
        utm_medium: str | None = None,
        utm_campaign: str | None = None,
        landing_page: str | None = None,
        promo_code: str | None = None,
        discount_kopecks: int = 0,
    ) -> "MarketingAttribution":
        if discount_kopecks < 0:
            raise InvalidOrder("Знижка не може бути відʼємною")
        return cls(
            order_source=order_source,
            utm_source=_clean_str(utm_source, 120),
            utm_medium=_clean_str(utm_medium, 120),
            utm_campaign=_clean_str(utm_campaign, 160),
            landing_page=_clean_str(landing_page, 300),
            promo_code=_clean_str(promo_code, 64),
            discount_kopecks=discount_kopecks,
        )


def _clean_str(value: str | None, max_len: int) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned[:max_len] if cleaned else None


@dataclass(frozen=True, slots=True)
class OrderStatusEntry:
    id: uuid.UUID
    from_status: OrderStatus | None
    to_status: OrderStatus
    note: str
    changed_at: dt.datetime


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
    marketing: MarketingAttribution = field(default_factory=MarketingAttribution)
    internal_note: str = ""
    updated_at: dt.datetime | None = None
    status_history: tuple[OrderStatusEntry, ...] = field(default_factory=tuple)

    @classmethod
    def place(
        cls,
        *,
        customer: Customer,
        delivery: Delivery,
        items: list[OrderItem],
        payment_method: PaymentMethod,
        marketing: MarketingAttribution | None = None,
        internal_note: str = "",
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
        now = dt.datetime.now(dt.UTC)
        initial_entry = OrderStatusEntry(
            id=uuid.uuid4(),
            from_status=None,
            to_status=OrderStatus.NEW,
            note="Замовлення створено",
            changed_at=now,
        )
        return cls(
            id=uuid.uuid4(),
            customer=customer,
            delivery=delivery,
            items=tuple(merged.values()),
            payment_method=payment_method,
            status=OrderStatus.NEW,
            created_at=now,
            updated_at=now,
            marketing=marketing or MarketingAttribution(),
            internal_note=internal_note.strip(),
            status_history=(initial_entry,),
        )

    def assign_number(self, number: int) -> None:
        if self.number is not None:
            raise InvalidOrder("Order number is already assigned")
        self.number = number

    def change_status(self, new_status: OrderStatus, *, note: str = "") -> OrderStatusEntry | None:
        if new_status == self.status:
            return None
        now = dt.datetime.now(dt.UTC)
        entry = OrderStatusEntry(
            id=uuid.uuid4(),
            from_status=self.status,
            to_status=new_status,
            note=note.strip()[:300],
            changed_at=now,
        )
        self.status = new_status
        self.updated_at = now
        self.status_history = (*self.status_history, entry)
        return entry

    def update_salon_details(
        self,
        *,
        internal_note: str | None = None,
        delivery_date: dt.date | None = None,
        time_slot: str | None = None,
        address: str | None = None,
    ) -> None:
        if internal_note is not None:
            self.internal_note = internal_note.strip()
        new_date = self.delivery.date if delivery_date is None else delivery_date
        new_slot = (
            self.delivery.time_slot
            if time_slot is None
            else ((time_slot.strip() or None) if time_slot is not None else None)
        )
        new_addr = (
            self.delivery.address
            if address is None
            else ((address.strip() or None) if address is not None else None)
        )
        if self.delivery.method is DeliveryMethod.TAXI and new_addr is None:
            raise AddressRequired
        self.delivery = Delivery(
            method=self.delivery.method,
            address=new_addr if self.delivery.method is DeliveryMethod.TAXI else None,
            date=new_date,
            time_slot=new_slot,
        )
        self.updated_at = dt.datetime.now(dt.UTC)

    @property
    def subtotal(self) -> Money:
        total = Money(0)
        for item in self.items:
            total = total + item.total
        return total

    @property
    def total(self) -> Money:
        sub = self.subtotal.kopecks
        disc = min(sub, self.marketing.discount_kopecks)
        return Money(max(0, sub - disc))
