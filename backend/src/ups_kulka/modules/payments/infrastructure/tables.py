"""ORM tables of the payments module (specs/006-payments/plan.md)."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ups_kulka.shared.infrastructure.db import Base


class PaymentRow(Base):
    __tablename__ = "payments_payments"
    __table_args__ = (
        CheckConstraint("amount_kopecks > 0", name="amount_positive"),
        # Order page and admin: payment status of an order.
        Index("ix_payments_payments_order_id", "order_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    # No FK: orders_orders belongs to another module (AGENTS.md, section 3).
    order_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    order_number: Mapped[int] = mapped_column(Integer)
    amount_kopecks: Mapped[int] = mapped_column(Integer)
    provider: Mapped[str] = mapped_column(String(32))
    # Webhook lookup by invoice id.
    invoice_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    page_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
