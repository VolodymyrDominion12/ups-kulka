import re
import uuid
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum

from ups_kulka.modules.catalog.domain.errors import InvalidProduct, InvalidSlug, InvalidTag
from ups_kulka.shared.domain.money import Money
from ups_kulka.shared.domain.transliteration import to_slug

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 200
MAX_IMAGES_PER_PRODUCT = 10
RELATED_PRODUCTS_LIMIT = 8
STANDARD_IMAGE_WIDTHS = (320, 640, 960, 1280)


@dataclass(frozen=True, slots=True)
class Slug:
    """URL-safe identifier in Latin (official Ukrainian transliteration)."""

    value: str

    def __post_init__(self) -> None:
        if not 3 <= len(self.value) <= 120 or not _SLUG_RE.fullmatch(self.value):
            raise InvalidSlug(
                f"Invalid slug '{self.value}': use 3-120 chars a-z, 0-9 and single hyphens"
            )

    def __str__(self) -> str:
        return self.value

    @classmethod
    def base_from_name(cls, name: str) -> str:
        raw = to_slug(name)
        if len(raw) < 3:
            raw = f"kompozytsiia-{raw}" if raw else "kompozytsiia"
        return raw[:110].strip("-")


class TagGroup(StrEnum):
    OCCASION = "occasion"  # день народження, виписка, 14 лютого
    RECIPIENT = "recipient"  # для дівчинки, для хлопчика, для мами
    AGE = "age"
    COLOR = "color"  # пастельні, золото-чорні
    THEME = "theme"  # єдиноріг, космос
    TYPE = "type"  # цифри, фонтан, бокс-сюрприз


class ProductSort(StrEnum):
    NEWEST = "newest"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"


# A collection page is indexed only with unique text AND this many active products.
MIN_PRODUCTS_FOR_INDEXING = 6
MAX_FAQ_ITEMS = 20
SEO_TITLE_MAX_LENGTH = 160
SEO_DESCRIPTION_MAX_LENGTH = 300


@dataclass(frozen=True, slots=True)
class FaqItem:
    question: str
    answer: str


@dataclass(frozen=True, slots=True)
class Tag:
    id: uuid.UUID
    group: TagGroup
    slug: Slug
    name: str
    seo_title: str = ""
    seo_description: str = ""
    intro_text: str = ""
    seo_text: str = ""
    faq: tuple[FaqItem, ...] = ()

    @classmethod
    def create(cls, *, group: TagGroup, slug: str, name: str) -> "Tag":
        clean_name = name.strip()
        if not clean_name:
            raise InvalidTag("Tag name cannot be empty")
        return cls(id=uuid.uuid4(), group=group, slug=Slug(slug), name=clean_name)

    @property
    def has_unique_text(self) -> bool:
        return bool(self.seo_text.strip())

    def is_indexable(self, product_count: int) -> bool:
        """A collection is indexed only with unique text AND enough products."""
        return self.has_unique_text and product_count >= MIN_PRODUCTS_FOR_INDEXING

    def with_seo(
        self,
        *,
        seo_title: str = "",
        seo_description: str = "",
        intro_text: str = "",
        seo_text: str = "",
        faq: tuple[FaqItem, ...] = (),
    ) -> "Tag":
        clean_title = seo_title.strip()
        clean_description = seo_description.strip()
        clean_intro = intro_text.strip()
        clean_text = seo_text.strip()
        if len(clean_title) > SEO_TITLE_MAX_LENGTH:
            raise InvalidTag(f"seo_title is longer than {SEO_TITLE_MAX_LENGTH} chars")
        if len(clean_description) > SEO_DESCRIPTION_MAX_LENGTH:
            raise InvalidTag(f"seo_description is longer than {SEO_DESCRIPTION_MAX_LENGTH} chars")
        items = tuple(faq)
        if len(items) > MAX_FAQ_ITEMS:
            raise InvalidTag(f"FAQ cannot have more than {MAX_FAQ_ITEMS} items")
        cleaned_faq: list[FaqItem] = []
        for item in items:
            question = item.question.strip()
            answer = item.answer.strip()
            if not question or not answer:
                raise InvalidTag("FAQ items must have both a question and an answer")
            cleaned_faq.append(FaqItem(question=question, answer=answer))
        return replace(
            self,
            seo_title=clean_title,
            seo_description=clean_description,
            intro_text=clean_intro,
            seo_text=clean_text,
            faq=tuple(cleaned_faq),
        )


@dataclass(frozen=True, slots=True)
class ProductImage:
    media_id: uuid.UUID
    position: int
    url_prefix: str
    blur_data_url: str
    width: int
    height: int

    @property
    def variants(self) -> dict[str, str]:
        result = {f"{w}w": f"{self.url_prefix}/{w}w.webp" for w in STANDARD_IMAGE_WIDTHS}
        result["original"] = f"{self.url_prefix}/original.webp"
        return result


@dataclass(slots=True)
class Product:
    id: uuid.UUID
    slug: Slug
    name: str
    description: str
    price: Money
    is_active: bool
    created_at: datetime
    tags: tuple[Tag, ...] = field(default_factory=tuple)
    old_price: Money | None = None
    images: tuple[ProductImage, ...] = field(default_factory=tuple)
    updated_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        slug: str,
        name: str,
        description: str,
        price: Money,
        tags: tuple[Tag, ...] = (),
        old_price: Money | None = None,
        images: tuple[ProductImage, ...] = (),
        is_active: bool = True,
    ) -> "Product":
        clean_name = _validate_product_fields(
            name=name,
            price=price,
            old_price=old_price,
            images=images,
        )
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            slug=Slug(slug),
            name=clean_name,
            description=description.strip(),
            price=price,
            old_price=old_price,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            tags=tags,
            images=images,
        )

    def update(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        price: Money | None = None,
        old_price: Money | None = None,
        clear_old_price: bool = False,
        is_active: bool | None = None,
        tags: tuple[Tag, ...] | None = None,
        images: tuple[ProductImage, ...] | None = None,
    ) -> None:
        new_name = self.name if name is None else name
        new_price = self.price if price is None else price
        if clear_old_price:
            new_old_price = None
        else:
            new_old_price = self.old_price if old_price is None else old_price
        new_images = self.images if images is None else images

        clean_name = _validate_product_fields(
            name=new_name,
            price=new_price,
            old_price=new_old_price,
            images=new_images,
        )
        self.name = clean_name
        if description is not None:
            self.description = description.strip()
        self.price = new_price
        self.old_price = new_old_price
        if is_active is not None:
            self.is_active = is_active
        if tags is not None:
            self.tags = tags
        if images is not None:
            self.images = new_images
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(UTC)


def _validate_product_fields(
    *,
    name: str,
    price: Money,
    old_price: Money | None,
    images: tuple[ProductImage, ...],
) -> str:
    clean_name = name.strip()
    if not clean_name:
        raise InvalidProduct("Product name cannot be empty")
    if len(clean_name) > MAX_NAME_LENGTH:
        raise InvalidProduct(f"Product name is longer than {MAX_NAME_LENGTH} chars")
    if price.is_zero:
        raise InvalidProduct("Product price must be greater than zero")
    if old_price is not None and old_price.kopecks <= price.kopecks:
        raise InvalidProduct("Old price must be greater than current price")
    if len(images) > MAX_IMAGES_PER_PRODUCT:
        raise InvalidProduct(f"Product can have at most {MAX_IMAGES_PER_PRODUCT} images")
    return clean_name
