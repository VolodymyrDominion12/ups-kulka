from ups_kulka.modules.catalog.domain.entities import (
    Product,
    ProductImage,
    Slug,
    Tag,
    TagGroup,
)
from ups_kulka.modules.catalog.infrastructure.tables import (
    ProductMediaRow,
    ProductRow,
    TagRow,
)
from ups_kulka.shared.domain.money import Money


def tag_to_domain(row: TagRow) -> Tag:
    return Tag(id=row.id, group=TagGroup(row.group), slug=Slug(row.slug), name=row.name)


def media_row_to_domain(row: ProductMediaRow) -> ProductImage:
    return ProductImage(
        media_id=row.media_id,
        position=row.position,
        url_prefix=row.url_prefix,
        blur_data_url=row.blur_data_url,
        width=row.width,
        height=row.height,
    )


def product_to_domain(row: ProductRow) -> Product:
    """``row.tags`` and ``row.media`` must be loaded eagerly (selectinload) before mapping."""
    return Product(
        id=row.id,
        slug=Slug(row.slug),
        name=row.name,
        description=row.description,
        price=Money(row.price_kopecks),
        old_price=Money(row.old_price_kopecks) if row.old_price_kopecks is not None else None,
        is_active=row.is_active,
        created_at=row.created_at,
        updated_at=row.updated_at,
        tags=tuple(tag_to_domain(tag) for tag in sorted(row.tags, key=lambda t: t.slug)),
        images=tuple(
            media_row_to_domain(m) for m in sorted(row.media, key=lambda item: item.position)
        ),
    )
