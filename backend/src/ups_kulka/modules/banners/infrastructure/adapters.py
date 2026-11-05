import uuid
from collections.abc import Sequence

from ups_kulka.modules.admin_auth.application.public import AdminAuthFacade
from ups_kulka.modules.banners.application.dto import BannerImageDTO
from ups_kulka.modules.catalog.application.public import CatalogFacade
from ups_kulka.modules.media.application.public import MediaFacade


class MediaBannerAdapter:
    def __init__(self, media: MediaFacade) -> None:
        self._media = media

    async def get_images(self, ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, BannerImageDTO]:
        assets = await self._media.get_assets(ids)
        return {
            mid: BannerImageDTO(
                url_prefix=asset.url_prefix,
                blur_data_url=asset.blur_data_url,
                width=asset.width,
                height=asset.height,
                variants=asset.variants,
            )
            for mid, asset in assets.items()
        }


class CatalogTagAdapter:
    def __init__(self, catalog: CatalogFacade) -> None:
        self._catalog = catalog

    async def existing_slugs(self, slugs: Sequence[str]) -> set[str]:
        return await self._catalog.existing_tag_slugs(slugs)


class BannerAdminAuthAdapter:
    def __init__(self, auth: AdminAuthFacade) -> None:
        self._auth = auth

    def require_admin(self, token: str | None) -> None:
        self._auth.verify_token(token)
