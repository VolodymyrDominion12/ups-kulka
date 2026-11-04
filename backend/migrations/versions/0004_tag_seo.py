"""tag SEO fields for collection landing pages (specs/002-collections-seo)

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-04

Adds to catalog_tags: seo_title, seo_description, intro_text, seo_text, faq (JSONB).
No new indexes: tags are few and the tag_id join is already covered by
ix_catalog_product_tags_tag_id and the product_tags composite PK.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "catalog_tags",
        sa.Column("seo_title", sa.String(length=160), server_default="", nullable=False),
    )
    op.add_column(
        "catalog_tags",
        sa.Column("seo_description", sa.String(length=300), server_default="", nullable=False),
    )
    op.add_column(
        "catalog_tags",
        sa.Column("intro_text", sa.Text(), server_default="", nullable=False),
    )
    op.add_column(
        "catalog_tags",
        sa.Column("seo_text", sa.Text(), server_default="", nullable=False),
    )
    op.add_column(
        "catalog_tags",
        sa.Column(
            "faq",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.alter_column("catalog_tags", "seo_title", server_default=None)
    op.alter_column("catalog_tags", "seo_description", server_default=None)
    op.alter_column("catalog_tags", "intro_text", server_default=None)
    op.alter_column("catalog_tags", "seo_text", server_default=None)
    op.alter_column("catalog_tags", "faq", server_default=None)


def downgrade() -> None:
    op.drop_column("catalog_tags", "faq")
    op.drop_column("catalog_tags", "seo_text")
    op.drop_column("catalog_tags", "intro_text")
    op.drop_column("catalog_tags", "seo_description")
    op.drop_column("catalog_tags", "seo_title")
