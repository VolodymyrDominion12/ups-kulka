"""Moves product photos from the old site through the media pipeline (specs/010)."""

import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from urllib.parse import urlparse

from ups_kulka.modules.catalog.application.legacy_import import LegacyPhoto
from ups_kulka.modules.catalog.application.ports import (
    CatalogUnitOfWorkFactory,
    MediaCatalogLookup,
    PhotoDownloader,
    PhotoUploader,
)
from ups_kulka.modules.catalog.application.use_cases.create_product import (
    resolve_product_images,
)
from ups_kulka.modules.catalog.domain.errors import ProductNotFound
from ups_kulka.shared.domain.errors import DomainError

logger = logging.getLogger("ups_kulka.catalog.import")


@dataclass(slots=True)
class PhotoImportReport:
    imported: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)  # already has photos
    failed: dict[str, str] = field(default_factory=dict)  # slug -> reason


class ImportLegacyPhotos:
    def __init__(
        self,
        uow_factory: CatalogUnitOfWorkFactory,
        media_lookup: MediaCatalogLookup,
        downloader: PhotoDownloader,
        uploader: PhotoUploader,
    ) -> None:
        self._uow_factory = uow_factory
        self._media_lookup = media_lookup
        self._downloader = downloader
        self._uploader = uploader

    async def __call__(self, photos: Sequence[LegacyPhoto]) -> PhotoImportReport:
        report = PhotoImportReport()
        for photo in photos:
            slug = photo.product_slug
            try:
                if await self._import_one(photo):
                    report.imported.append(slug)
                else:
                    report.skipped.append(slug)
            except DomainError as exc:  # image too small, not an image, product missing
                report.failed[slug] = exc.message
            except Exception as exc:  # network errors: one bad photo must not stop the rest
                logger.warning("photo import failed for %s: %s", slug, exc)
                report.failed[slug] = f"{type(exc).__name__}: {exc}"
        return report

    async def _import_one(self, photo: LegacyPhoto) -> bool:
        async with self._uow_factory() as uow:
            product = await uow.products.get_by_slug(photo.product_slug, active_only=False)
        if product is None:
            raise ProductNotFound(photo.product_slug)
        if product.images:
            return False

        content = await self._downloader.fetch(photo.image_url)
        media_id = await self._uploader.upload(_filename(photo.image_url), content)
        images = await resolve_product_images([media_id], self._media_lookup)

        async with self._uow_factory() as uow:
            current = await uow.products.get_by_id(product.id)
            if current is None:
                raise ProductNotFound(photo.product_slug)
            if current.images:  # attached by someone else meanwhile
                return False
            current.update(images=images)
            await uow.products.save(current)
            await uow.commit()
        return True


def _filename(url: str) -> str:
    name = urlparse(url).path.rsplit("/", 1)[-1]
    return name or "photo.jpg"
