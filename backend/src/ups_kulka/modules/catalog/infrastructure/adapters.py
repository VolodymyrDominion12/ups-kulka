import uuid
from collections.abc import Sequence

from ups_kulka.modules.admin_auth.application.public import AdminAuthFacade
from ups_kulka.modules.catalog.application.ports import MediaSnapshot
from ups_kulka.modules.media.application.public import MediaFacade


class CatalogAdminAuthAdapter:
    def __init__(self, auth: AdminAuthFacade) -> None:
        self._auth = auth

    def require_admin(self, token: str | None) -> None:
        self._auth.verify_token(token)


class MediaCatalogAdapter:
    def __init__(self, media: MediaFacade) -> None:
        self._media = media

    async def get_media_snapshots(self, ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, MediaSnapshot]:
        assets = await self._media.get_assets(ids)
        return {
            mid: MediaSnapshot(
                media_id=asset.id,
                url_prefix=asset.url_prefix,
                blur_data_url=asset.blur_data_url,
                width=asset.width,
                height=asset.height,
            )
            for mid, asset in assets.items()
        }
