"""ORM tables of the orders module (specs/004-checkout, specs/007-admin, specs/011-analytics).

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


class OrderStatusHistoryRow(Base):
    __tablename__ = "orders_status_history"
    __table_args__ = (Index("ix_orders_status_history_order_id", "order_id", "changed_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("orders_orders.id", ondelete="CASCADE")
    )
    from_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    to_status: Mapped[str] = mapped_column(String(16))
    note: Mapped[str] = mapped_column(String(300), default="")
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class OrderRow(Base):
    __tablename__ = "orders_orders"
    __table_args__ = (
        CheckConstraint("total_kopecks >= 0", name="total_not_negative"),
        CheckConstraint("discount_kopecks >= 0", name="discount_not_negative"),
        Index("ix_orders_orders_status_created", "status", "created_at"),
        Index("ix_orders_orders_delivery_date", "delivery_date", "created_at"),
        Index("ix_orders_orders_created_at", "created_at"),
        Index("ix_orders_orders_customer_phone", "customer_phone", "created_at"),
    )
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
    order_source: Mapped[str] = mapped_column(String(32), default="storefront")
    utm_source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(String(120), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(160), nullable=True)
    landing_page: Mapped[str | None] = mapped_column(String(300), nullable=True)
    promo_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    discount_kopecks: Mapped[int] = mapped_column(Integer, default=0)
    total_kopecks: Mapped[int] = mapped_column(Integer)
    internal_note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    items: Mapped[list[OrderItemRow]] = relationship(lazy="raise")
    status_history: Mapped[list[OrderStatusHistoryRow]] = relationship(
        lazy="raise",
        order_by=OrderStatusHistoryRow.changed_at,
    )
