"""ORM tables of the catalog module.

Rules (see AGENTS.md, section 5):
- every foreign key has an index;
- relationships use lazy="raise", load them explicitly with selectinload().
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ups_kulka.shared.infrastructure.db import Base

product_tags = Table(
    "catalog_product_tags",
    Base.metadata,
    Column(
        "product_id",
        Uuid,
        ForeignKey("catalog_products.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Uuid,
        ForeignKey("catalog_tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    # The PK (product_id, tag_id) covers product_id; tag_id needs its own index.
    Index("ix_catalog_product_tags_tag_id", "tag_id"),
)


class TagRow(Base):
    __tablename__ = "catalog_tags"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    group: Mapped[str] = mapped_column(String(32))
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    name: Mapped[str] = mapped_column(String(120))


class ProductMediaRow(Base):
    __tablename__ = "catalog_product_media"
    __table_args__ = (
        CheckConstraint("position >= 0", name="product_media_position_non_negative"),
        CheckConstraint("width > 0 AND height > 0", name="product_media_dimensions_positive"),
        # The composite PK (product_id, position) indexes the FK product_id.
        Index("ix_catalog_product_media_media_id", "media_id"),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("catalog_products.id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    # No FK to media_assets (belongs to another module, see AGENTS.md section 3).
    media_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    url_prefix: Mapped[str] = mapped_column(String(255))
    blur_data_url: Mapped[str] = mapped_column(Text)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)


class ProductRow(Base):
    __tablename__ = "catalog_products"
    __table_args__ = (
        CheckConstraint("price_kopecks > 0", name="price_positive"),
        CheckConstraint(
            "old_price_kopecks IS NULL OR old_price_kopecks > price_kopecks",
            name="old_price_greater_than_price",
        ),
        # Storefront list: WHERE is_active ORDER BY created_at DESC, id DESC
        Index(
            "ix_catalog_products_active_created",
            "is_active",
            "created_at",
            "id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    price_kopecks: Mapped[int] = mapped_column(Integer)
    old_price_kopecks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    tags: Mapped[list[TagRow]] = relationship(secondary=product_tags, lazy="raise")
    media: Mapped[list[ProductMediaRow]] = relationship(
        lazy="raise",
        order_by=ProductMediaRow.position,
        cascade="all, delete-orphan",
    )
