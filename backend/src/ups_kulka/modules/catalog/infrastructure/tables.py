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


class ProductRow(Base):
    __tablename__ = "catalog_products"
    __table_args__ = (
        CheckConstraint("price_kopecks > 0", name="price_positive"),
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
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    tags: Mapped[list[TagRow]] = relationship(secondary=product_tags, lazy="raise")
