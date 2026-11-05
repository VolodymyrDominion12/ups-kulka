"""ORM tables of the banners module (specs/017-home-banners/plan.md)."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ups_kulka.shared.infrastructure.db import Base


class BannerCampaignRow(Base):
    __tablename__ = "banners_campaigns"
    __table_args__ = (
        CheckConstraint(
            "layout IN ('balloons', 'image', 'split', 'collection')", name="layout_valid"
        ),
        CheckConstraint("status IN ('draft', 'published')", name="status_valid"),
        CheckConstraint("ends_at > starts_at", name="period_valid"),
        Index("ix_banners_campaigns_active", "status", "starts_at", "ends_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    layout: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(12))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    priority: Mapped[int] = mapped_column(Integer)
    headline: Mapped[str] = mapped_column(String(120))
    subtitle: Mapped[str] = mapped_column(String(300))
    cta_label: Mapped[str] = mapped_column(String(40))
    cta_url: Mapped[str] = mapped_column(String(255))
    cta2_label: Mapped[str] = mapped_column(String(40))
    cta2_url: Mapped[str] = mapped_column(String(255))
    media_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    media_mobile_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    image_alt: Mapped[str] = mapped_column(String(255))
    theme: Mapped[str] = mapped_column(String(20))
    tag_slug: Mapped[str | None] = mapped_column(String(120))
    ribbon_text: Mapped[str] = mapped_column(String(160))
    ribbon_url: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
