"""HTTP schemas of orders. They define the OpenAPI contract for the storefront."""

import datetime as dt
import uuid
from typing import Literal

from pydantic import BaseModel, Field

from ups_kulka.modules.orders.application.dto import (
    CheckoutOptionsDTO,
    OrderLineInput,
    PlacedOrderDTO,
    PlaceOrderCommand,
)


class CustomerIn(BaseModel):
    name: str = Field(min_length=1, max_length=120, examples=["Олена"])
    phone: str = Field(min_length=10, max_length=20, examples=["093 111 22 33"])
    comment: str = Field(default="", max_length=1000, examples=["Напис «З днем народження, Соня»"])


class DeliveryIn(BaseModel):
    method: Literal["pickup", "taxi"] = Field(
        description="taxi: the shop sends a taxi, the customer pays the fare separately"
    )
    address: str | None = Field(default=None, max_length=300, examples=["вул. Хрещатик, 1, кв. 5"])
    date: dt.date | None = None
    time_slot: str | None = Field(default=None, max_length=20, examples=["14–16"])


class OrderLineIn(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(ge=1, le=99)


class PlaceOrderIn(BaseModel):
    customer: CustomerIn
    delivery: DeliveryIn
    payment_method: Literal["on_delivery", "online"] = "on_delivery"
    items: list[OrderLineIn] = Field(min_length=1, max_length=50)

    def to_command(self) -> PlaceOrderCommand:
        return PlaceOrderCommand(
            customer_name=self.customer.name,
            phone=self.customer.phone,
            comment=self.customer.comment,
            delivery_method=self.delivery.method,
            address=self.delivery.address,
            delivery_date=self.delivery.date,
            time_slot=self.delivery.time_slot,
            payment_method=self.payment_method,
            lines=tuple(OrderLineInput(i.product_id, i.quantity) for i in self.items),
        )


class PlacedOrderItemOut(BaseModel):
    product_id: uuid.UUID
    product_name: str
    unit_price_kopecks: int
    quantity: int
    total_kopecks: int


class PlacedOrderOut(BaseModel):
    id: uuid.UUID
    number: int
    total_kopecks: int = Field(description="Goods only; the taxi fare is paid separately")
    delivery_method: str
    payment_method: str
    payment_url: str | None = Field(description="Payment page when payment_method is online")
    items: list[PlacedOrderItemOut]

    @classmethod
    def from_dto(cls, dto: PlacedOrderDTO) -> "PlacedOrderOut":
        return cls(
            id=dto.id,
            number=dto.number,
            total_kopecks=dto.total_kopecks,
            delivery_method=dto.delivery_method,
            payment_method=dto.payment_method,
            payment_url=dto.payment_url,
            items=[
                PlacedOrderItemOut(
                    product_id=i.product_id,
                    product_name=i.product_name,
                    unit_price_kopecks=i.unit_price_kopecks,
                    quantity=i.quantity,
                    total_kopecks=i.total_kopecks,
                )
                for i in dto.items
            ],
        )


class CheckoutOptionsOut(BaseModel):
    delivery_methods: list[str]
    payment_methods: list[str]

    @classmethod
    def from_dto(cls, dto: CheckoutOptionsDTO) -> "CheckoutOptionsOut":
        return cls(
            delivery_methods=list(dto.delivery_methods),
            payment_methods=list(dto.payment_methods),
        )
