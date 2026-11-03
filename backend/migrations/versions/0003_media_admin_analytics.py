"""media pipeline, admin catalog/orders, and marketing analytics

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-03

Indexes (specs/009-media-pipeline/plan.md, specs/007-admin/plan.md, specs/011-analytics/plan.md):
- media_assets: PK (id) + ix created_at;
- catalog_product_media: PK (product_id, position) covering FK product_id + ix media_id;
- orders_orders: ix (status, created_at), ix (delivery_date, created_at),
  ix created_at, ix (customer_phone, created_at);
- orders_status_history: ix (order_id, changed_at) covering FK order_id.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "media_assets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=64), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("url_prefix", sa.String(length=255), nullable=False),
        sa.Column("blur_data_url", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "file_size_bytes > 0",
            name=op.f("ck_media_assets_media_file_size_positive"),
        ),
        sa.CheckConstraint(
            "width > 0 AND height > 0",
            name=op.f("ck_media_assets_media_dimensions_positive"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_media_assets")),
    )
    op.create_index("ix_media_assets_created_at", "media_assets", ["created_at"], unique=False)

    op.add_column("catalog_products", sa.Column("old_price_kopecks", sa.Integer(), nullable=True))
    op.add_column(
        "catalog_products",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.alter_column("catalog_products", "updated_at", server_default=None)
    op.create_check_constraint(
        op.f("ck_catalog_products_old_price_greater_than_price"),
        "catalog_products",
        "old_price_kopecks IS NULL OR old_price_kopecks > price_kopecks",
    )

    op.create_table(
        "catalog_product_media",
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("media_id", sa.Uuid(), nullable=False),
        sa.Column("url_prefix", sa.String(length=255), nullable=False),
        sa.Column("blur_data_url", sa.Text(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "position >= 0",
            name=op.f("ck_catalog_product_media_product_media_position_non_negative"),
        ),
        sa.CheckConstraint(
            "width > 0 AND height > 0",
            name=op.f("ck_catalog_product_media_product_media_dimensions_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["catalog_products.id"],
            name=op.f("fk_catalog_product_media_product_id_catalog_products"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("product_id", "position", name=op.f("pk_catalog_product_media")),
    )
    op.create_index(
        "ix_catalog_product_media_media_id",
        "catalog_product_media",
        ["media_id"],
        unique=False,
    )

    op.add_column(
        "orders_orders",
        sa.Column(
            "order_source",
            sa.String(length=32),
            server_default="storefront",
            nullable=False,
        ),
    )
    op.alter_column("orders_orders", "order_source", server_default=None)
    op.add_column(
        "orders_orders",
        sa.Column("utm_source", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "orders_orders",
        sa.Column("utm_medium", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "orders_orders",
        sa.Column("utm_campaign", sa.String(length=160), nullable=True),
    )
    op.add_column(
        "orders_orders",
        sa.Column("landing_page", sa.String(length=300), nullable=True),
    )
    op.add_column(
        "orders_orders",
        sa.Column("promo_code", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "orders_orders",
        sa.Column(
            "discount_kopecks",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
    op.alter_column("orders_orders", "discount_kopecks", server_default=None)
    op.add_column(
        "orders_orders",
        sa.Column(
            "internal_note",
            sa.Text(),
            server_default="",
            nullable=False,
        ),
    )
    op.alter_column("orders_orders", "internal_note", server_default=None)
    op.add_column(
        "orders_orders",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.alter_column("orders_orders", "updated_at", server_default=None)
    op.create_check_constraint(
        op.f("ck_orders_orders_discount_not_negative"),
        "orders_orders",
        "discount_kopecks >= 0",
    )
    op.create_index(
        "ix_orders_orders_status_created",
        "orders_orders",
        ["status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_orders_orders_delivery_date",
        "orders_orders",
        ["delivery_date", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_orders_orders_created_at",
        "orders_orders",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_orders_orders_customer_phone",
        "orders_orders",
        ["customer_phone", "created_at"],
        unique=False,
    )

    op.create_table(
        "orders_status_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("from_status", sa.String(length=16), nullable=True),
        sa.Column("to_status", sa.String(length=16), nullable=False),
        sa.Column("note", sa.String(length=300), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders_orders.id"],
            name=op.f("fk_orders_status_history_order_id_orders_orders"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders_status_history")),
    )
    op.create_index(
        "ix_orders_status_history_order_id",
        "orders_status_history",
        ["order_id", "changed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_orders_status_history_order_id", table_name="orders_status_history")
    op.drop_table("orders_status_history")

    op.drop_index("ix_orders_orders_customer_phone", table_name="orders_orders")
    op.drop_index("ix_orders_orders_created_at", table_name="orders_orders")
    op.drop_index("ix_orders_orders_delivery_date", table_name="orders_orders")
    op.drop_index("ix_orders_orders_status_created", table_name="orders_orders")
    op.drop_constraint(
        op.f("ck_orders_orders_discount_not_negative"),
        "orders_orders",
        type_="check",
    )
    op.drop_column("orders_orders", "updated_at")
    op.drop_column("orders_orders", "internal_note")
    op.drop_column("orders_orders", "discount_kopecks")
    op.drop_column("orders_orders", "promo_code")
    op.drop_column("orders_orders", "landing_page")
    op.drop_column("orders_orders", "utm_campaign")
    op.drop_column("orders_orders", "utm_medium")
    op.drop_column("orders_orders", "utm_source")
    op.drop_column("orders_orders", "order_source")

    op.drop_index("ix_catalog_product_media_media_id", table_name="catalog_product_media")
    op.drop_table("catalog_product_media")

    op.drop_constraint(
        op.f("ck_catalog_products_old_price_greater_than_price"),
        "catalog_products",
        type_="check",
    )
    op.drop_column("catalog_products", "updated_at")
    op.drop_column("catalog_products", "old_price_kopecks")

    op.drop_index("ix_media_assets_created_at", table_name="media_assets")
    op.drop_table("media_assets")
