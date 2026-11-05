"""banner campaigns: index for the admin list (specs/017-home-banners)

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-05

ix_banners_campaigns_starts_at: admin list `ORDER BY starts_at DESC LIMIT n`.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_banners_campaigns_starts_at", "banners_campaigns", ["starts_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_banners_campaigns_starts_at", table_name="banners_campaigns")
