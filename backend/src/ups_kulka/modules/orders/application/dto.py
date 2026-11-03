import uuid
from dataclasses import dataclass
from datetime import date

from ups_kulka.modules.orders.domain.entities import Order


@dataclass(frozen=True, slots=True)
class OrderLineInput:
    product_id: uuid.UUID
    quantity: int


@dataclass(frozen=True, slots=True)
class PlaceOrderCommand:
    customer_name: str
    phone: str
    delivery_method: str
    payment_method: str
    lines: tuple[OrderLineInput, ...]
    address: str | None = None
    delivery_date: date | None = None
    time_slot: str | None = None
    comment: str = ""


@dataclass(frozen=True, slots=True)
class CatalogProduct:
    """What orders needs to know about a product (filled by the catalog facade adapter)."""

    id: uuid.UUID
    name: str
    price_kopecks: int
    is_active: bool


@dataclass(frozen=True, slots=True)
class PlacedOrderItemDTO:
    product_id: uuid.UUID
    product_name: str
    unit_price_kopecks: int
    quantity: int
    total_kopecks: int


@dataclass(frozen=True, slots=True)
class PlacedOrderDTO:
    id: uuid.UUID
    number: int
    total_kopecks: int
    delivery_method: str
    payment_method: str
    payment_url: str | None
    items: tuple[PlacedOrderItemDTO, ...]

    @classmethod
    def from_entity(cls, order: Order, payment_url: str | None) -> "PlacedOrderDTO":
        if order.number is None:
            raise ValueError("order must be saved before it is returned")
        return cls(
            id=order.id,
            number=order.number,
            total_kopecks=order.total.kopecks,
            delivery_method=order.delivery.method.value,
            payment_method=order.payment_method.value,
            payment_url=payment_url,
            items=tuple(
                PlacedOrderItemDTO(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    unit_price_kopecks=item.unit_price.kopecks,
                    quantity=item.quantity,
                    total_kopecks=item.total.kopecks,
                )
                for item in order.items
            ),
        )


@dataclass(frozen=True, slots=True)
class CheckoutOptionsDTO:
    delivery_methods: tuple[str, ...]
    payment_methods: tuple[str, ...]
