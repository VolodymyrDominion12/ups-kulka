from ups_kulka.modules.catalog.domain.entities import Product, Slug, Tag, TagGroup
from ups_kulka.modules.catalog.infrastructure.tables import ProductRow, TagRow
from ups_kulka.shared.domain.money import Money


def tag_to_domain(row: TagRow) -> Tag:
    return Tag(id=row.id, group=TagGroup(row.group), slug=Slug(row.slug), name=row.name)


def product_to_domain(row: ProductRow) -> Product:
    """``row.tags`` must be loaded eagerly (selectinload) before mapping."""
    return Product(
        id=row.id,
        slug=Slug(row.slug),
        name=row.name,
        description=row.description,
        price=Money(row.price_kopecks),
        is_active=row.is_active,
        created_at=row.created_at,
        tags=tuple(tag_to_domain(tag) for tag in sorted(row.tags, key=lambda t: t.slug)),
    )
