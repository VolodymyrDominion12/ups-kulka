"""ORM tables of the orders module (specs/004-checkout/plan.md).

Every FK has an index; relationships are lazy="raise".
"""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ups_kulka.shared.infrastructure.db import Base


class OrderItemRow(Base):
    __tablename__ = "orders_order_items"
    __table_args__ = (
        CheckConstraint("quantity BETWEEN 1 AND 99", name="quantity_range"),
        CheckConstraint("unit_price_kopecks > 0", name="unit_price_positive"),
        Index("ix_orders_order_items_order_id", "order_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("orders_orders.id", ondelete="CASCADE")
    )
    # No FK: catalog_products belongs to another module; name/price are a snapshot.
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    product_name: Mapped[str] = mapped_column(String(200))
    unit_price_kopecks: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)


class OrderRow(Base):
    __tablename__ = "orders_orders"
    __table_args__ = (CheckConstraint("total_kopecks >= 0", name="total_not_negative"),)
    # Fetch the IDENTITY number in the INSERT ... RETURNING, no extra SELECT.
    __mapper_args__ = {"eager_defaults": True}  # noqa: RUF012 - SQLAlchemy API

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    # Human-friendly number for the customer and the shop; lookup by number in admin.
    number: Mapped[int] = mapped_column(Integer, Identity(start=1001), unique=True)
    status: Mapped[str] = mapped_column(String(16))
    customer_name: Mapped[str] = mapped_column(String(120))
    customer_phone: Mapped[str] = mapped_column(String(13))
    comment: Mapped[str] = mapped_column(Text, default="")
    delivery_method: Mapped[str] = mapped_column(String(16))
    delivery_address: Mapped[str | None] = mapped_column(String(300))
    delivery_date: Mapped[date | None] = mapped_column(Date)
    delivery_slot: Mapped[str | None] = mapped_column(String(20))
    payment_method: Mapped[str] = mapped_column(String(16))
    total_kopecks: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    items: Mapped[list[OrderItemRow]] = relationship(lazy="raise")
