from ups_kulka.shared.domain.errors import ConflictError, NotFoundError, ValidationError


class InvalidSlug(ValidationError):
    code = "invalid_slug"


class InvalidProduct(ValidationError):
    code = "invalid_product"


class InvalidTag(ValidationError):
    code = "invalid_tag"


class TagSlugAlreadyTaken(ConflictError):
    code = "tag_slug_already_taken"

    def __init__(self, slug: str) -> None:
        super().__init__(f"Tag slug '{slug}' is already taken")


class UnknownTags(ValidationError):
    code = "unknown_tags"

    def __init__(self, slugs: list[str]) -> None:
        super().__init__(f"Unknown tags: {', '.join(sorted(slugs))}")
        self.slugs = slugs


class ProductNotFound(NotFoundError):
    code = "product_not_found"

    def __init__(self, slug: str) -> None:
        super().__init__(f"Product '{slug}' not found")


class SlugAlreadyTaken(ConflictError):
    code = "slug_already_taken"

    def __init__(self, slug: str) -> None:
        super().__init__(f"Slug '{slug}' is already taken")


class UnknownMediaAssets(ValidationError):
    code = "unknown_media_assets"

    def __init__(self, ids: list[str]) -> None:
        super().__init__(f"Unknown media assets: {', '.join(ids)}")
        self.ids = ids


class PhotoUnavailable(ValidationError):
    """An external photo could not be fetched (missing, too big, not an image)."""

    code = "photo_unavailable"
