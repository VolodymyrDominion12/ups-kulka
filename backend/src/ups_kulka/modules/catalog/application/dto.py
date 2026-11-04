import uuid
from dataclasses import dataclass, field
from datetime import datetime

from ups_kulka.modules.catalog.domain.entities import FaqItem, Product, ProductImage, Tag


@dataclass(frozen=True, slots=True)
class CreateTagCommand:
    group: str
    slug: str
    name: str
    seo_title: str = ""
    seo_description: str = ""
    intro_text: str = ""
    seo_text: str = ""
    faq: tuple["FaqItemDTO", ...] = ()


@dataclass(frozen=True, slots=True)
class UpdateTagSeoCommand:
    tag_id: uuid.UUID
    seo_title: str = ""
    seo_description: str = ""
    intro_text: str = ""
    seo_text: str = ""
    faq: tuple["FaqItemDTO", ...] = ()
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class CreateProductCommand:
    slug: str
    name: str
    description: str
    price_kopecks: int
    tag_slugs: tuple[str, ...] = field(default_factory=tuple)
    old_price_kopecks: int | None = None
    media_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class QuickCreateProductCommand:
    """Express salon product creation: slug is optional (auto-transliterated from name)."""

    name: str
    price_kopecks: int
    description: str = ""
    slug: str | None = None
    old_price_kopecks: int | None = None
    is_active: bool = True
    tag_slugs: tuple[str, ...] = field(default_factory=tuple)
    media_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateProductCommand:
    product_id: uuid.UUID
    name: str | None = None
    description: str | None = None
    price_kopecks: int | None = None
    old_price_kopecks: int | None = None
    clear_old_price: bool = False
    is_active: bool | None = None
    tag_slugs: tuple[str, ...] | None = None
    media_ids: tuple[uuid.UUID, ...] | None = None
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class ListProductsQuery:
    tag_slug: str | None = None
    limit: int = 24
    offset: int = 0
    q: str | None = None
    sort: str = "newest"
    on_sale: bool | None = None


@dataclass(frozen=True, slots=True)
class ListAdminProductsQuery:
    q: str | None = None
    tag_slug: str | None = None
    is_active: bool | None = None
    limit: int = 24
    offset: int = 0
    auth_token: str | None = None


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
class FaqItemDTO:
    question: str
    answer: str

    @classmethod
    def from_entity(cls, item: FaqItem) -> "FaqItemDTO":
        return cls(question=item.question, answer=item.answer)


@dataclass(frozen=True, slots=True)
class TagSummaryDTO:
    id: uuid.UUID
    group: str
    slug: str
    name: str
    product_count: int
    is_indexable: bool

    @classmethod
    def from_entity(cls, tag: Tag, product_count: int) -> "TagSummaryDTO":
        return cls(
            id=tag.id,
            group=tag.group.value,
            slug=tag.slug.value,
            name=tag.name,
            product_count=product_count,
            is_indexable=tag.is_indexable(product_count),
        )


@dataclass(frozen=True, slots=True)
class TagDetailDTO:
    id: uuid.UUID
    group: str
    slug: str
    name: str
    seo_title: str
    seo_description: str
    intro_text: str
    seo_text: str
    faq: tuple[FaqItemDTO, ...]
    product_count: int
    is_indexable: bool

    @classmethod
    def from_entity(cls, tag: Tag, product_count: int) -> "TagDetailDTO":
        return cls(
            id=tag.id,
            group=tag.group.value,
            slug=tag.slug.value,
            name=tag.name,
            seo_title=tag.seo_title,
            seo_description=tag.seo_description,
            intro_text=tag.intro_text,
            seo_text=tag.seo_text,
            faq=tuple(FaqItemDTO.from_entity(item) for item in tag.faq),
            product_count=product_count,
            is_indexable=tag.is_indexable(product_count),
        )


@dataclass(frozen=True, slots=True)
class ProductImageDTO:
    media_id: uuid.UUID
    position: int
    url_prefix: str
    blur_data_url: str
    width: int
    height: int
    variants: dict[str, str]

    @classmethod
    def from_entity(cls, img: ProductImage) -> "ProductImageDTO":
        return cls(
            media_id=img.media_id,
            position=img.position,
            url_prefix=img.url_prefix,
            blur_data_url=img.blur_data_url,
            width=img.width,
            height=img.height,
            variants=img.variants,
        )


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
    old_price_kopecks: int | None = None
    images: tuple[ProductImageDTO, ...] = field(default_factory=tuple)

    @classmethod
    def from_entity(cls, product: Product) -> "ProductDTO":
        return cls(
            id=product.id,
            slug=product.slug.value,
            name=product.name,
            description=product.description,
            price_kopecks=product.price.kopecks,
            old_price_kopecks=product.old_price.kopecks if product.old_price else None,
            is_active=product.is_active,
            created_at=product.created_at,
            tags=tuple(TagDTO.from_entity(tag) for tag in product.tags),
            images=tuple(ProductImageDTO.from_entity(img) for img in product.images),
        )


@dataclass(frozen=True, slots=True)
class ProductForOrder:
    """Lightweight read model for checkout: no tags, no description."""

    id: uuid.UUID
    name: str
    price_kopecks: int
    is_active: bool


@dataclass(frozen=True, slots=True)
class ProductAnalyticsInfo:
    """Read model for marketing analytics: tags and basic metadata."""

    id: uuid.UUID
    slug: str
    name: str
    price_kopecks: int
    is_active: bool
    created_at: datetime
    tags: tuple[TagDTO, ...]
