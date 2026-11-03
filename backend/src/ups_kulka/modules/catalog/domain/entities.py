import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from ups_kulka.modules.catalog.domain.errors import InvalidProduct, InvalidSlug, InvalidTag
from ups_kulka.shared.domain.money import Money

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 200


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


class TagGroup(StrEnum):
    OCCASION = "occasion"  # день народження, виписка, 14 лютого
    RECIPIENT = "recipient"  # для дівчинки, для хлопчика, для мами
    AGE = "age"
    COLOR = "color"  # пастельні, золото-чорні
    THEME = "theme"  # єдиноріг, космос
    TYPE = "type"  # цифри, фонтан, бокс-сюрприз


@dataclass(frozen=True, slots=True)
class Tag:
    id: uuid.UUID
    group: TagGroup
    slug: Slug
    name: str

    @classmethod
    def create(cls, *, group: TagGroup, slug: str, name: str) -> "Tag":
        clean_name = name.strip()
        if not clean_name:
            raise InvalidTag("Tag name cannot be empty")
        return cls(id=uuid.uuid4(), group=group, slug=Slug(slug), name=clean_name)


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

    @classmethod
    def create(
        cls,
        *,
        slug: str,
        name: str,
        description: str,
        price: Money,
        tags: tuple[Tag, ...] = (),
    ) -> "Product":
        clean_name = name.strip()
        if not clean_name:
            raise InvalidProduct("Product name cannot be empty")
        if len(clean_name) > MAX_NAME_LENGTH:
            raise InvalidProduct(f"Product name is longer than {MAX_NAME_LENGTH} chars")
        if price.is_zero:
            raise InvalidProduct("Product price must be greater than zero")
        return cls(
            id=uuid.uuid4(),
            slug=Slug(slug),
            name=clean_name,
            description=description.strip(),
            price=price,
            is_active=True,
            created_at=datetime.now(UTC),
            tags=tags,
        )

    def deactivate(self) -> None:
        self.is_active = False
