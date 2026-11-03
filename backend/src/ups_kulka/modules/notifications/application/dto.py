from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True, slots=True)
class NoticeLine:
    name: str
    quantity: int
    total_kopecks: int


@dataclass(frozen=True, slots=True)
class OrderPlacedNotice:
    number: int
    lines: tuple[NoticeLine, ...]
    total_kopecks: int
    customer_name: str
    customer_phone: str
    delivery_method: str  # "pickup" | "taxi"
    payment_method: str  # "on_delivery" | "online"
    address: str | None = None
    delivery_date: date | None = None
    time_slot: str | None = None
    comment: str = ""
    payment_url: str | None = field(default=None)


@dataclass(frozen=True, slots=True)
class PaymentReceivedNotice:
    order_number: int
    amount_kopecks: int
