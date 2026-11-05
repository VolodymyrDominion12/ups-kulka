"""banner campaigns: manual "show now" override (specs/017-home-banners)

Revision ID: 0008
Revises: 0007
Create Date: 2026-11-05

pinned: the admin can show one campaign right now, ignoring its dates. The partial
unique index uq_banners_campaigns_pinned guarantees at most one such campaign, and
also serves the storefront lookup "pinned campaign first".

pinned=false for existing rows, then the server default is dropped: the application
always writes the value explicitly.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "banners_campaigns",
        sa.Column("pinned", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("banners_campaigns", "pinned", server_default=None)
    op.create_index(
        "uq_banners_campaigns_pinned",
        "banners_campaigns",
        ["pinned"],
        unique=True,
        postgresql_where=sa.text("pinned"),
    )


def downgrade() -> None:
    op.drop_index("uq_banners_campaigns_pinned", table_name="banners_campaigns")
    op.drop_column("banners_campaigns", "pinned")
