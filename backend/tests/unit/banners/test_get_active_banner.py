import uuid
from datetime import UTC, datetime
from types import TracebackType
from typing import Self

from ups_kulka.modules.banners.application.dto import BannerImageDTO
from ups_kulka.modules.banners.application.use_cases.get_active_banner import GetActiveBanner
from ups_kulka.modules.banners.domain.entities import (
    BannerCampaign,
    BannerLayout,
    BannerStatus,
)

NOW = datetime(2027, 3, 5, 12, tzinfo=UTC)
IMAGE = BannerImageDTO(
    url_prefix="/media/x", blur_data_url="data:", width=1600, height=800, variants={}
)


class FakeBanners:
    def __init__(self, campaigns: list[BannerCampaign]) -> None:
        self._campaigns = campaigns

    async def add(self, campaign: BannerCampaign) -> None:
        self._campaigns.append(campaign)

    async def get_active(self, now: datetime) -> BannerCampaign | None:
        active = [c for c in self._campaigns if c.is_active_at(now)]
        return max(active, key=lambda c: (c.priority, c.starts_at), default=None)


class FakeUow:
    def __init__(self, campaigns: list[BannerCampaign]) -> None:
        self.banners = FakeBanners(campaigns)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...


class FakeMedia:
    def __init__(self, known: dict[uuid.UUID, BannerImageDTO]) -> None:
        self._known = known

    async def get_images(self, ids: list[uuid.UUID]) -> dict[uuid.UUID, BannerImageDTO]:  # type: ignore[override]
        return {i: self._known[i] for i in ids if i in self._known}


def campaign(**overrides: object) -> BannerCampaign:
    params: dict[str, object] = {
        "name": "c",
        "layout": BannerLayout.BALLOONS,
        "starts_at": datetime(2027, 3, 1, tzinfo=UTC),
        "ends_at": datetime(2027, 3, 9, tzinfo=UTC),
        "headline": "H",
        "status": BannerStatus.PUBLISHED,
    }
    params.update(overrides)
    return BannerCampaign.create(**params)  # type: ignore[arg-type]


def build(
    campaigns: list[BannerCampaign], known: dict[uuid.UUID, BannerImageDTO] | None = None
) -> GetActiveBanner:
    return GetActiveBanner(
        uow_factory=lambda: FakeUow(campaigns),  # type: ignore[arg-type,return-value]
        media=FakeMedia(known or {}),  # type: ignore[arg-type]
        clock=lambda: NOW,
    )


async def test_no_campaign_returns_default_balloons() -> None:
    banner = await build([])()
    assert banner.layout is BannerLayout.BALLOONS
    assert banner.campaign_id is None


async def test_draft_campaign_is_ignored() -> None:
    banner = await build([campaign(status=BannerStatus.DRAFT)])()
    assert banner.campaign_id is None


async def test_higher_priority_wins() -> None:
    low = campaign(headline="low", priority=1)
    high = campaign(headline="high", priority=5)
    banner = await build([low, high])()
    assert banner.headline == "high"


async def test_image_campaign_includes_images() -> None:
    media_id, mobile_id = uuid.uuid4(), uuid.uuid4()
    known = {media_id: IMAGE, mobile_id: IMAGE}
    active = campaign(layout=BannerLayout.IMAGE, media_id=media_id, media_mobile_id=mobile_id)
    banner = await build([active], known)()
    assert banner.layout is BannerLayout.IMAGE
    assert banner.image == IMAGE
    assert banner.image_mobile == IMAGE


async def test_missing_photo_falls_back_to_default() -> None:
    active = campaign(layout=BannerLayout.IMAGE, media_id=uuid.uuid4())
    banner = await build([active])()
    assert banner.campaign_id is None
    assert banner.layout is BannerLayout.BALLOONS


async def test_missing_mobile_photo_is_tolerated() -> None:
    media_id = uuid.uuid4()
    active = campaign(layout=BannerLayout.IMAGE, media_id=media_id, media_mobile_id=uuid.uuid4())
    banner = await build([active], {media_id: IMAGE})()
    assert banner.image == IMAGE
    assert banner.image_mobile is None
