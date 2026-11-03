"""Public facade of the media module for other modules (e.g. catalog)."""

import uuid
from collections.abc import Sequence

from ups_kulka.modules.media.application.dto import MediaAssetDTO, UploadMediaCommand
from ups_kulka.modules.media.application.ports import MediaUnitOfWorkFactory
from ups_kulka.modules.media.application.use_cases.upload_media import UploadMedia

__all__ = ["MediaAssetDTO", "MediaFacade"]


class MediaFacade:
    def __init__(
        self, uow_factory: MediaUnitOfWorkFactory, upload: UploadMedia | None = None
    ) -> None:
        self._uow_factory = uow_factory
        self._upload = upload

    async def get_assets(self, ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, MediaAssetDTO]:
        unique_ids = list(dict.fromkeys(ids))
        if not unique_ids:
            return {}
        async with self._uow_factory() as uow:
            assets = await uow.media.get_many(unique_ids)
        return {asset.id: MediaAssetDTO.from_entity(asset) for asset in assets}

    async def import_photo(self, filename: str, content: bytes) -> MediaAssetDTO:
        """Trusted server-side upload (no admin token): used by other modules and scripts,
        never exposed over HTTP. Same pipeline as the admin upload."""
        if self._upload is None:
            raise RuntimeError("MediaFacade was built without an uploader")
        return await self._upload(
            UploadMediaCommand(filename=filename, content_type="", content=content)
        )
