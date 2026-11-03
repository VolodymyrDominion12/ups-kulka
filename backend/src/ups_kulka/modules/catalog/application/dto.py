import uuid
from dataclasses import dataclass, field
from datetime import datetime

from ups_kulka.modules.catalog.domain.entities import Product, Tag


@dataclass(frozen=True, slots=True)
class CreateTagCommand:
    group: str
    slug: str
    name: str


@dataclass(frozen=True, slots=True)
class CreateProductCommand:
    slug: str
    name: str
    description: str
    price_kopecks: int
    tag_slugs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ListProductsQuery:
    tag_slug: str | None = None
    limit: int = 24
    offset: int = 0


@dataclass(frozen=True, slots=True)
class TagDTO:
    id: uuid.UUID
    group: str
    slug: str
    name: str

    @classmethod
    def from_entity(cls, tag: Tag) -> "TagDTO":
        return cls(id=tag.id, group=tag.group.value, slug=tag.slug.value, name=tag.name)


@dataclass(frozen=True, slots=True)
class ProductDTO:
    id: uuid.UUID
    slug: str
    name: str
    description: str
    price_kopecks: int
    is_active: bool
    created_at: datetime
    tags: tuple[TagDTO, ...]

    @classmethod
    def from_entity(cls, product: Product) -> "ProductDTO":
        return cls(
            id=product.id,
            slug=product.slug.value,
            name=product.name,
            description=product.description,
            price_kopecks=product.price.kopecks,
            is_active=product.is_active,
            created_at=product.created_at,
            tags=tuple(TagDTO.from_entity(tag) for tag in product.tags),
        )
