"""Ready holiday campaigns offered in the admin (specs/017-home-banners)."""

from collections.abc import Callable
from datetime import datetime

from ups_kulka.modules.banners.application.dto import BannerPresetDTO, ListBannerPresetsQuery
from ups_kulka.modules.banners.application.ports import AdminGuard
from ups_kulka.modules.banners.application.use_cases.get_active_banner import utc_now
from ups_kulka.modules.banners.domain.presets import HOLIDAY_PRESETS, HolidayPreset


def _to_dto(preset: HolidayPreset, now: datetime) -> BannerPresetDTO:
    starts_at, ends_at = preset.period(now)
    return BannerPresetDTO(
        key=preset.key,
        title=preset.title,
        description=preset.description,
        name=preset.campaign_name(now),
        layout=preset.layout,
        theme=preset.theme,
        headline=preset.headline,
        subtitle=preset.subtitle,
        starts_at=starts_at,
        ends_at=ends_at,
        priority=preset.priority,
        cta_label=preset.cta_label,
        cta_url=preset.cta_url,
        cta2_label=preset.cta2_label,
        cta2_url=preset.cta2_url,
        ribbon_text=preset.ribbon_text,
        ribbon_url=preset.ribbon_url,
    )


class ListBannerPresets:
    """Four fixed holidays with dates for the nearest season; no database involved."""

    def __init__(self, auth: AdminGuard, clock: Callable[[], datetime] = utc_now) -> None:
        self._auth = auth
        self._clock = clock

    async def __call__(self, query: ListBannerPresetsQuery) -> list[BannerPresetDTO]:
        self._auth.require_admin(query.auth_token)
        now = self._clock()
        return [_to_dto(preset, now) for preset in HOLIDAY_PRESETS]
