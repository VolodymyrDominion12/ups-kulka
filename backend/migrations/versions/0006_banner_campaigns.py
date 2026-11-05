"""home banner campaigns (specs/017-home-banners)

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-05

Index ix_banners_campaigns_active (status, starts_at, ends_at): the storefront query
"published campaign covering now, highest priority first". The table holds a handful of
rows per year, so priority is sorted in memory (no need to widen the index).
No foreign keys: media ids point to another module's table (public facade only).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "banners_campaigns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("layout", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("headline", sa.String(length=120), nullable=False),
        sa.Column("subtitle", sa.String(length=300), nullable=False),
        sa.Column("cta_label", sa.String(length=40), nullable=False),
        sa.Column("cta_url", sa.String(length=255), nullable=False),
        sa.Column("cta2_label", sa.String(length=40), nullable=False),
        sa.Column("cta2_url", sa.String(length=255), nullable=False),
        sa.Column("media_id", sa.Uuid(), nullable=True),
        sa.Column("media_mobile_id", sa.Uuid(), nullable=True),
        sa.Column("image_alt", sa.String(length=255), nullable=False),
        sa.Column("theme", sa.String(length=20), nullable=False),
        sa.Column("tag_slug", sa.String(length=120), nullable=True),
        sa.Column("ribbon_text", sa.String(length=160), nullable=False),
        sa.Column("ribbon_url", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "layout IN ('balloons', 'image', 'split', 'collection')",
            name=op.f("ck_banners_campaigns_layout_valid"),
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'published')",
            name=op.f("ck_banners_campaigns_status_valid"),
        ),
        sa.CheckConstraint("ends_at > starts_at", name=op.f("ck_banners_campaigns_period_valid")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_banners_campaigns")),
    )
    op.create_index(
        "ix_banners_campaigns_active",
        "banners_campaigns",
        ["status", "starts_at", "ends_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_banners_campaigns_active", table_name="banners_campaigns")
    op.drop_table("banners_campaigns")
