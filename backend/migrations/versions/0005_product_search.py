"""product search: pg_trgm + GIN indexes (specs/014-search-sort)

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-04

Adds pg_trgm extension and GIN trigram indexes on catalog_products.name and
catalog_products.description to accelerate ILIKE '%q%' search.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_index(
        "ix_catalog_products_name_trgm",
        "catalog_products",
        ["name"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_catalog_products_description_trgm",
        "catalog_products",
        ["description"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"description": "gin_trgm_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_catalog_products_description_trgm", table_name="catalog_products")
    op.drop_index("ix_catalog_products_name_trgm", table_name="catalog_products")
    # pg_trgm extension is left installed (dropping it may fail while in use).
