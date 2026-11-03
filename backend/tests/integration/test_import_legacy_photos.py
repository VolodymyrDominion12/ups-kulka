"""Integration test: old-site photos go through the real media pipeline (specs/010)."""

import io
from pathlib import Path

import pytest
from dependency_injector import providers
from PIL import Image

from ups_kulka.container import Container
from ups_kulka.modules.catalog.application.dto import CreateProductCommand
from ups_kulka.modules.catalog.application.legacy_import import LegacyPhoto
from ups_kulka.modules.catalog.domain.errors import PhotoUnavailable
from ups_kulka.modules.media.infrastructure.imaging import LocalFileMediaStorage

pytestmark = pytest.mark.integration


def _jpeg(width: int, height: int) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(230, 179, 179)).save(buf, format="JPEG")
    return buf.getvalue()


class StubDownloader:
    def __init__(self, files: dict[str, bytes]) -> None:
        self.files = files

    async def fetch(self, url: str) -> bytes:
        if url not in self.files:
            raise PhotoUnavailable(f"{url} відповів 404")
        return self.files[url]


async def test_imports_photos_and_is_idempotent(container: Container, tmp_path: Path) -> None:
    container.media.storage.override(providers.Object(LocalFileMediaStorage(str(tmp_path))))
    container.catalog.photo_downloader.override(
        providers.Object(
            StubDownloader(
                {
                    "https://old/img/drakon.jpg": _jpeg(800, 1000),
                    "https://old/img/lev.jpg": _jpeg(40, 40),  # too small for the pipeline
                }
            )
        )
    )
    create = container.catalog.create_product()
    for slug in ("drakon", "lev", "kit"):
        await create(
            CreateProductCommand(slug=slug, name=slug, description="", price_kopecks=10000)
        )

    photos = [
        LegacyPhoto(product_slug="drakon", image_url="https://old/img/drakon.jpg"),
        LegacyPhoto(product_slug="lev", image_url="https://old/img/lev.jpg"),
        LegacyPhoto(product_slug="kit", image_url="https://old/img/kit.jpg"),
    ]
    report = await container.catalog.import_legacy_photos()(photos)

    assert report.imported == ["drakon"]
    assert set(report.failed) == {"lev", "kit"}
    assert "404" in report.failed["kit"]

    product = await container.catalog.get_product()("drakon")
    assert len(product.images) == 1
    assert product.images[0].url_prefix.startswith("/media/")

    again = await container.catalog.import_legacy_photos()(photos[:1])
    assert again.skipped == ["drakon"]
