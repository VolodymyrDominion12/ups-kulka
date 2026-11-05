from datetime import UTC, datetime

import pytest

from tests.fakes.banners import FakeAdminGuard
from ups_kulka.modules.banners.application.dto import BannerPresetDTO, ListBannerPresetsQuery
from ups_kulka.modules.banners.application.use_cases.list_banner_presets import ListBannerPresets
from ups_kulka.modules.banners.domain.entities import BannerCampaign
from ups_kulka.modules.banners.domain.presets import KYIV
from ups_kulka.shared.domain.errors import UnauthorizedError

NOW = datetime(2026, 11, 5, 12, tzinfo=UTC)


async def presets(now: datetime = NOW) -> dict[str, BannerPresetDTO]:
    use_case = ListBannerPresets(auth=FakeAdminGuard(), clock=lambda: now)
    items = await use_case(ListBannerPresetsQuery(auth_token="good"))
    return {item.key: item for item in items}


def local_dates(starts_at: datetime, ends_at: datetime) -> tuple[str, str]:
    return (
        starts_at.astimezone(KYIV).date().isoformat(),
        ends_at.astimezone(KYIV).date().isoformat(),
    )


async def test_four_holidays_with_unique_keys_and_names() -> None:
    items = await presets()
    assert list(items) == ["valentines", "march_8", "christmas", "new_year"]
    assert len({item.name for item in items.values()}) == 4


async def test_dates_are_the_nearest_season_in_kyiv() -> None:
    items = await presets()
    expected = {
        "valentines": ("2027-02-01", "2027-02-15"),
        "march_8": ("2027-03-01", "2027-03-10"),
        "christmas": ("2026-12-18", "2026-12-26"),
        "new_year": ("2026-12-26", "2027-01-03"),
    }
    for key, dates in expected.items():
        preset = items[key]
        assert local_dates(preset.starts_at, preset.ends_at) == dates


async def test_names_use_the_celebration_year() -> None:
    items = await presets()
    assert items["new_year"].name == "Новий рік 2027"
    assert items["christmas"].name == "Різдво 2026"
    assert items["march_8"].name == "8 Березня 2027"


async def test_inside_a_window_keeps_the_current_season() -> None:
    items = await presets(datetime(2027, 2, 10, 12, tzinfo=UTC))
    assert local_dates(items["valentines"].starts_at, items["valentines"].ends_at) == (
        "2027-02-01",
        "2027-02-15",
    )


async def test_after_a_window_moves_to_the_next_year() -> None:
    items = await presets(datetime(2027, 2, 20, 12, tzinfo=UTC))
    assert local_dates(items["valentines"].starts_at, items["valentines"].ends_at) == (
        "2028-02-01",
        "2028-02-15",
    )


async def test_new_year_window_still_runs_on_january_2_kyiv_time() -> None:
    # 2 Jan 2027, 00:30 Kyiv = 1 Jan 2027, 22:30 UTC.
    items = await presets(datetime(2027, 1, 1, 22, 30, tzinfo=UTC))
    assert local_dates(items["new_year"].starts_at, items["new_year"].ends_at) == (
        "2026-12-26",
        "2027-01-03",
    )


async def test_presets_pass_domain_validation() -> None:
    for preset in (await presets()).values():
        campaign = BannerCampaign.create(
            name=preset.name,
            layout=preset.layout,
            theme=preset.theme,
            starts_at=preset.starts_at,
            ends_at=preset.ends_at,
            headline=preset.headline,
            subtitle=preset.subtitle,
            cta_label=preset.cta_label,
            cta_url=preset.cta_url,
            cta2_label=preset.cta2_label,
            cta2_url=preset.cta2_url,
            ribbon_text=preset.ribbon_text,
            ribbon_url=preset.ribbon_url,
            priority=preset.priority,
        )
        assert campaign.ends_at > campaign.starts_at


async def test_presets_require_admin() -> None:
    use_case = ListBannerPresets(auth=FakeAdminGuard(), clock=lambda: NOW)
    with pytest.raises(UnauthorizedError):
        await use_case(ListBannerPresetsQuery(auth_token=None))
