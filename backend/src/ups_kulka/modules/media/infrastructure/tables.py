"""ORM tables of the media module (specs/009-media-pipeline/plan.md)."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ups_kulka.shared.infrastructure.db import Base


class MediaAssetRow(Base):
    __tablename__ = "media_assets"
    __table_args__ = (
        CheckConstraint("file_size_bytes > 0", name="media_file_size_positive"),
        CheckConstraint("width > 0 AND height > 0", name="media_dimensions_positive"),
        Index("ix_media_assets_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(64))
    file_size_bytes: Mapped[int] = mapped_column(Integer)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    url_prefix: Mapped[str] = mapped_column(String(255))
    blur_data_url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
