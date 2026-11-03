import uuid

import pytest

from tests.fakes.catalog import FakeCatalogUnitOfWork, FakeMediaLookup
from ups_kulka.modules.catalog.application.dto import CreateProductCommand
from ups_kulka.modules.catalog.application.legacy_import import LegacyPhoto
from ups_kulka.modules.catalog.application.use_cases.create_product import CreateProduct
from ups_kulka.modules.catalog.application.use_cases.import_legacy_photos import (
    ImportLegacyPhotos,
)
from ups_kulka.modules.catalog.domain.errors import PhotoUnavailable
from ups_kulka.modules.media.domain.errors import ImageTooSmall


class FakeDownloader:
    def __init__(self, broken: set[str] | None = None) -> None:
        self.broken = broken or set()
        self.calls: list[str] = []

    async def fetch(self, url: str) -> bytes:
        self.calls.append(url)
        if url in self.broken:
            raise PhotoUnavailable(f"{url} відповів 404")
        return b"jpeg-bytes"


class FakeUploader:
    """Registers each upload in the media lookup, like the real media module."""

    def __init__(self, lookup: FakeMediaLookup, too_small: set[str] | None = None) -> None:
        self.lookup = lookup
        self.too_small = too_small or set()
        self.filenames: list[str] = []

    async def upload(self, filename: str, content: bytes) -> uuid.UUID:
        if filename in self.too_small:
            raise ImageTooSmall
        self.filenames.append(filename)
        media_id = uuid.uuid4()
        self.lookup.snapshots.update(FakeMediaLookup(media_id).snapshots)
        return media_id


async def _seed(uow: FakeCatalogUnitOfWork, *slugs: str) -> None:
    for slug in slugs:
        await CreateProduct(uow)(
            CreateProductCommand(slug=slug, name=slug, description="", price_kopecks=10000)
        )


def _photo(slug: str) -> LegacyPhoto:
    return LegacyPhoto(product_slug=slug, image_url=f"https://old.example/img/p/{slug}.jpg")


@pytest.fixture
def uow() -> FakeCatalogUnitOfWork:
    return FakeCatalogUnitOfWork()


async def test_attaches_photo_through_media_pipeline(uow: FakeCatalogUnitOfWork) -> None:
    await _seed(uow, "drakon", "lev")
    lookup = FakeMediaLookup()
    uploader = FakeUploader(lookup)
    use_case = ImportLegacyPhotos(uow, lookup, FakeDownloader(), uploader)

    report = await use_case([_photo("drakon"), _photo("lev")])

    assert report.imported == ["drakon", "lev"]
    assert report.failed == {}
    assert uploader.filenames == ["drakon.jpg", "lev.jpg"]
    image = uow.committed_products["drakon"].images[0]
    assert image.url_prefix.startswith("/media/")
    assert image.position == 0


async def test_second_run_skips_products_with_photos(uow: FakeCatalogUnitOfWork) -> None:
    await _seed(uow, "drakon")
    lookup = FakeMediaLookup()
    downloader = FakeDownloader()
    use_case = ImportLegacyPhotos(uow, lookup, downloader, FakeUploader(lookup))

    await use_case([_photo("drakon")])
    report = await use_case([_photo("drakon")])

    assert report.skipped == ["drakon"]
    assert len(downloader.calls) == 1  # nothing downloaded again


async def test_one_bad_photo_does_not_stop_the_rest(uow: FakeCatalogUnitOfWork) -> None:
    await _seed(uow, "drakon", "lev", "kit")
    lookup = FakeMediaLookup()
    downloader = FakeDownloader(broken={"https://old.example/img/p/drakon.jpg"})
    uploader = FakeUploader(lookup, too_small={"lev.jpg"})
    use_case = ImportLegacyPhotos(uow, lookup, downloader, uploader)

    report = await use_case([_photo("drakon"), _photo("lev"), _photo("kit"), _photo("nema")])

    assert report.imported == ["kit"]
    assert set(report.failed) == {"drakon", "lev", "nema"}
    assert "404" in report.failed["drakon"]
    assert "замале" in report.failed["lev"]
    assert uow.committed_products["drakon"].images == ()


async def test_unexpected_errors_are_reported(uow: FakeCatalogUnitOfWork) -> None:
    await _seed(uow, "drakon")

    class ExplodingDownloader:
        async def fetch(self, url: str) -> bytes:
            raise ConnectionResetError("reset by peer")

    lookup = FakeMediaLookup()
    report = await ImportLegacyPhotos(uow, lookup, ExplodingDownloader(), FakeUploader(lookup))(
        [_photo("drakon")]
    )
    assert report.failed == {"drakon": "ConnectionResetError: reset by peer"}
