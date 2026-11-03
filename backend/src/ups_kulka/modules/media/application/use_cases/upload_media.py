import uuid

from ups_kulka.modules.media.application.dto import MediaAssetDTO, UploadMediaCommand
from ups_kulka.modules.media.application.ports import (
    AdminGuard,
    ImageProcessor,
    MediaStorage,
    MediaUnitOfWorkFactory,
)
from ups_kulka.modules.media.domain.entities import MAX_FILE_SIZE_BYTES, MediaAsset
from ups_kulka.modules.media.domain.errors import InvalidMediaFile, MediaFileTooLarge


class UploadMedia:
    def __init__(
        self,
        uow_factory: MediaUnitOfWorkFactory,
        processor: ImageProcessor,
        storage: MediaStorage,
        auth: AdminGuard | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._processor = processor
        self._storage = storage
        self._auth = auth

    async def __call__(self, cmd: UploadMediaCommand) -> MediaAssetDTO:
        if self._auth is not None:
            self._auth.require_admin(cmd.auth_token)

        size = len(cmd.content)
        if size <= 0:
            raise InvalidMediaFile("Файл порожній")
        if size > MAX_FILE_SIZE_BYTES:
            raise MediaFileTooLarge

        processed = self._processor.process(cmd.content)
        asset_id = uuid.uuid4()
        asset = MediaAsset.create(
            asset_id=asset_id,
            original_filename=cmd.filename,
            mime_type=processed.mime_type,
            file_size_bytes=size,
            width=processed.width,
            height=processed.height,
            blur_data_url=processed.blur_data_url,
        )

        await self._storage.save_files(asset.id, processed.files)
        async with self._uow_factory() as uow:
            await uow.media.add(asset)
            await uow.commit()

        return MediaAssetDTO.from_entity(asset)
