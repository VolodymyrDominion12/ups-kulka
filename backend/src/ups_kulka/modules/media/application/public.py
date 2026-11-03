"""Public facade of the media module for other modules (e.g. catalog)."""

import uuid
from collections.abc import Sequence

from ups_kulka.modules.media.application.dto import MediaAssetDTO
from ups_kulka.modules.media.application.ports import MediaUnitOfWorkFactory

__all__ = ["MediaAssetDTO", "MediaFacade"]


class MediaFacade:
    def __init__(self, uow_factory: MediaUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def get_assets(self, ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, MediaAssetDTO]:
        unique_ids = list(dict.fromkeys(ids))
        if not unique_ids:
            return {}
        async with self._uow_factory() as uow:
            assets = await uow.media.get_many(unique_ids)
        return {asset.id: MediaAssetDTO.from_entity(asset) for asset in assets}
