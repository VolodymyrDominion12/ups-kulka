import uuid
from collections.abc import Callable, Sequence
from typing import Protocol

from ups_kulka.modules.media.application.dto import ProcessedImage
from ups_kulka.modules.media.domain.entities import MediaAsset
from ups_kulka.shared.application.pagination import Page, PageRequest
from ups_kulka.shared.application.uow import UnitOfWork


class AdminGuard(Protocol):
    def require_admin(self, token: str | None) -> None: ...


class ImageProcessor(Protocol):
    def process(self, raw_bytes: bytes) -> ProcessedImage:
        """Auto-orient EXIF, strip GPS/metadata, crop 4:5, build WebP variants & blurhash."""
        ...


class MediaStorage(Protocol):
    async def save_files(self, asset_id: uuid.UUID, files: dict[str, bytes]) -> None: ...


class MediaRepository(Protocol):
    async def add(self, asset: MediaAsset) -> None: ...

    async def get_many(self, ids: Sequence[uuid.UUID]) -> list[MediaAsset]:
        """Batch lookup in ONE query."""
        ...

    async def list_recent(self, page: PageRequest) -> Page[MediaAsset]: ...


class MediaUnitOfWork(UnitOfWork, Protocol):
    media: MediaRepository


type MediaUnitOfWorkFactory = Callable[[], MediaUnitOfWork]
