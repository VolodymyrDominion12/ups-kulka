import uuid
from collections.abc import Sequence

import httpx

from ups_kulka.modules.admin_auth.application.public import AdminAuthFacade
from ups_kulka.modules.catalog.application.ports import MediaSnapshot
from ups_kulka.modules.catalog.domain.errors import PhotoUnavailable
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


MAX_PHOTO_BYTES = 15 * 1024 * 1024  # same limit as the media pipeline


class HttpPhotoDownloader:
    """Downloads product photos from the old site (specs/010)."""

    def __init__(self, timeout: float = 20.0) -> None:
        self._timeout = timeout

    async def fetch(self, url: str) -> bytes:
        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                response = await client.get(url)
        except httpx.HTTPError as exc:
            raise PhotoUnavailable(f"Не вдалося завантажити {url}: {exc}") from exc
        if response.status_code != httpx.codes.OK:
            raise PhotoUnavailable(f"{url} відповів {response.status_code}")
        if not response.headers.get("content-type", "").startswith("image/"):
            raise PhotoUnavailable(f"{url} — не зображення")
        if len(response.content) > MAX_PHOTO_BYTES:
            raise PhotoUnavailable(f"{url} більший за 15 МБ")
        return response.content


class MediaPhotoUploader:
    def __init__(self, media: MediaFacade) -> None:
        self._media = media

    async def upload(self, filename: str, content: bytes) -> uuid.UUID:
        asset = await self._media.import_photo(filename, content)
        return asset.id
