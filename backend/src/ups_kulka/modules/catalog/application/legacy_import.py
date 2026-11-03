"""Turns the catalogue captured from the old site into catalog commands (specs/010).

Pure function: no I/O, so the mapping is unit-tested; the script only runs the commands.
"""

from collections import Counter
from dataclasses import dataclass
from typing import TypedDict

from ups_kulka.modules.catalog.application.dto import CreateProductCommand, CreateTagCommand
from ups_kulka.shared.domain.transliteration import to_slug


class LegacyTag(TypedDict):
    old_category: str
    group: str
    slug: str
    name: str


class LegacyProduct(TypedDict):
    old_id: int
    name: str
    price_uah: int
    old_price_uah: int | None
    image_url: str
    tag: str


class LegacyCatalog(TypedDict):
    tags: list[LegacyTag]
    products: list[LegacyProduct]


@dataclass(frozen=True, slots=True)
class LegacyPhoto:
    product_slug: str
    image_url: str


@dataclass(frozen=True, slots=True)
class LegacyImportPlan:
    tags: tuple[CreateTagCommand, ...]
    products: tuple[CreateProductCommand, ...]
    photos: tuple[LegacyPhoto, ...] = ()


def plan_legacy_import(catalog: LegacyCatalog) -> LegacyImportPlan:
    """Commands in a stable order: every tag (empty ones too), then products by old id,
    so the newest old product becomes the newest new one."""
    tags = tuple(
        CreateTagCommand(group=tag["group"], slug=tag["slug"], name=tag["name"])
        for tag in catalog["tags"]
    )
    products = sorted(catalog["products"], key=lambda p: p["old_id"])
    base_slugs = Counter(to_slug(p["name"]) for p in products)

    commands = []
    photos = []
    for product in products:
        slug = to_slug(product["name"])
        if base_slugs[slug] > 1 or len(slug) < 3:
            slug = f"{slug}-{product['old_id']}".strip("-")
        price = product["price_uah"] * 100
        old_price = (product["old_price_uah"] or 0) * 100
        commands.append(
            CreateProductCommand(
                slug=slug,
                name=product["name"],
                description="",
                price_kopecks=price,
                tag_slugs=(product["tag"],),
                # Only a real discount becomes a crossed-out price on the storefront.
                old_price_kopecks=old_price if old_price > price else None,
            )
        )
        if product["image_url"]:
            photos.append(LegacyPhoto(product_slug=slug, image_url=product["image_url"]))
    return LegacyImportPlan(tags=tags, products=tuple(commands), photos=tuple(photos))
