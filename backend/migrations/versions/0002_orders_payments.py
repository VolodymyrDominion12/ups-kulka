"""orders and payments

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-03

Indexes (specs/004-checkout/plan.md, specs/006-payments/plan.md):
- orders_orders: UNIQUE number (lookup by number), number is IDENTITY from 1001;
- orders_order_items: ix order_id (FK);
- payments_payments: UNIQUE invoice_id (webhook), ix order_id (payment status of an order).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "orders_orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("number", sa.Integer(), sa.Identity(always=False, start=1001), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("customer_name", sa.String(length=120), nullable=False),
        sa.Column("customer_phone", sa.String(length=13), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("delivery_method", sa.String(length=16), nullable=False),
        sa.Column("delivery_address", sa.String(length=300), nullable=True),
        sa.Column("delivery_date", sa.Date(), nullable=True),
        sa.Column("delivery_slot", sa.String(length=20), nullable=True),
        sa.Column("payment_method", sa.String(length=16), nullable=False),
        sa.Column("total_kopecks", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("total_kopecks >= 0", name=op.f("ck_orders_orders_total_not_negative")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders_orders")),
        sa.UniqueConstraint("number", name=op.f("uq_orders_orders_number")),
    )
    op.create_table(
        "orders_order_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("product_name", sa.String(length=200), nullable=False),
        sa.Column("unit_price_kopecks", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "quantity BETWEEN 1 AND 99", name=op.f("ck_orders_order_items_quantity_range")
        ),
        sa.CheckConstraint(
            "unit_price_kopecks > 0", name=op.f("ck_orders_order_items_unit_price_positive")
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders_orders.id"],
            name=op.f("fk_orders_order_items_order_id_orders_orders"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders_order_items")),
    )
    op.create_index(
        "ix_orders_order_items_order_id", "orders_order_items", ["order_id"], unique=False
    )
    op.create_table(
        "payments_payments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("amount_kopecks", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("invoice_id", sa.String(length=64), nullable=True),
        sa.Column("page_url", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount_kopecks > 0", name=op.f("ck_payments_payments_amount_positive")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_payments_payments")),
        sa.UniqueConstraint("invoice_id", name=op.f("uq_payments_payments_invoice_id")),
    )
    op.create_index(
        "ix_payments_payments_order_id", "payments_payments", ["order_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_payments_payments_order_id", table_name="payments_payments")
    op.drop_table("payments_payments")
    op.drop_index("ix_orders_order_items_order_id", table_name="orders_order_items")
    op.drop_table("orders_order_items")
    op.drop_table("orders_orders")
