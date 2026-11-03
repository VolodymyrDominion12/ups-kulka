"""catalog: products, tags, product_tags

Revision ID: 0001
Revises:
Create Date: 2026-11-03

Indexes (specs/001-catalog/plan.md):
- uq slug on products and tags;
- (is_active, created_at, id) for the storefront list;
- product_tags: PK (product_id, tag_id) + ix tag_id for "products by tag".
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "catalog_tags",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("group", sa.String(length=32), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_catalog_tags")),
        sa.UniqueConstraint("slug", name=op.f("uq_catalog_tags_slug")),
    )
    op.create_table(
        "catalog_products",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price_kopecks", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("price_kopecks > 0", name=op.f("ck_catalog_products_price_positive")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_catalog_products")),
        sa.UniqueConstraint("slug", name=op.f("uq_catalog_products_slug")),
    )
    op.create_index(
        "ix_catalog_products_active_created",
        "catalog_products",
        ["is_active", "created_at", "id"],
        unique=False,
    )
    op.create_table(
        "catalog_product_tags",
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["catalog_products.id"],
            name=op.f("fk_catalog_product_tags_product_id_catalog_products"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["catalog_tags.id"],
            name=op.f("fk_catalog_product_tags_tag_id_catalog_tags"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("product_id", "tag_id", name=op.f("pk_catalog_product_tags")),
    )
    op.create_index(
        "ix_catalog_product_tags_tag_id", "catalog_product_tags", ["tag_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_catalog_product_tags_tag_id", table_name="catalog_product_tags")
    op.drop_table("catalog_product_tags")
    op.drop_index("ix_catalog_products_active_created", table_name="catalog_products")
    op.drop_table("catalog_products")
    op.drop_table("catalog_tags")
