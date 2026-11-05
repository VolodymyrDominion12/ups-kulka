from collections.abc import Callable
from datetime import UTC, datetime

from ups_kulka.modules.banners.application.dto import HomeBannerDTO
from ups_kulka.modules.banners.application.ports import BannerUnitOfWorkFactory, MediaLookup
from ups_kulka.modules.banners.domain.entities import IMAGE_LAYOUTS


def utc_now() -> datetime:
    return datetime.now(UTC)


class GetActiveBanner:
    """Home hero for "now": the active campaign, or the default balloons hero."""

    def __init__(
        self,
        uow_factory: BannerUnitOfWorkFactory,
        media: MediaLookup,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._uow_factory = uow_factory
        self._media = media
        self._clock = clock

    async def __call__(self) -> HomeBannerDTO:
        async with self._uow_factory() as uow:
            campaign = await uow.banners.get_active(self._clock())
        if campaign is None:
            return HomeBannerDTO.default()

        media_ids = [mid for mid in (campaign.media_id, campaign.media_mobile_id) if mid]
        images = await self._media.get_images(media_ids) if media_ids else {}
        image = images.get(campaign.media_id) if campaign.media_id else None
        mobile = images.get(campaign.media_mobile_id) if campaign.media_mobile_id else None
        if campaign.layout in IMAGE_LAYOUTS and image is None:
            # The photo vanished: never show a broken hero, fall back to the default.
            return HomeBannerDTO.default()
        return HomeBannerDTO.from_campaign(campaign, image, mobile)
