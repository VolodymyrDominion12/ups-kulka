import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from tests.conftest import QueryCounter
from ups_kulka.container import Container
from ups_kulka.modules.banners.domain.entities import (
    BannerCampaign,
    BannerLayout,
    BannerStatus,
)

pytestmark = pytest.mark.integration

NOW = datetime.now(UTC)


async def _add(container: Container, **overrides: object) -> BannerCampaign:
    params: dict[str, object] = {
        "name": "c",
        "layout": BannerLayout.BALLOONS,
        "starts_at": NOW - timedelta(days=1),
        "ends_at": NOW + timedelta(days=1),
        "headline": "H",
        "status": BannerStatus.PUBLISHED,
    }
    params.update(overrides)
    campaign = BannerCampaign.create(**params)  # type: ignore[arg-type]
    async with container.banners.uow() as uow:
        await uow.banners.add(campaign)
        await uow.commit()
    return campaign


async def test_api_returns_default_when_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/storefront/home-banner")
    assert response.status_code == 200
    body = response.json()
    assert body["layout"] == "balloons"
    assert body["campaign_id"] is None
    assert "s-maxage=60" in response.headers["cache-control"]


async def test_api_returns_active_campaign(client: AsyncClient, container: Container) -> None:
    campaign = await _add(container, headline="З 8 Березня!", cta_label="Обрати", cta_url="/kulky")
    body = (await client.get("/api/v1/storefront/home-banner")).json()
    assert body["campaign_id"] == str(campaign.id)
    assert body["headline"] == "З 8 Березня!"
    assert body["cta_url"] == "/kulky"


async def test_selection_rules(container: Container) -> None:
    await _add(
        container,
        headline="expired",
        ends_at=NOW - timedelta(hours=1),
        starts_at=NOW - timedelta(days=2),
        priority=99,
    )
    await _add(
        container,
        headline="future",
        starts_at=NOW + timedelta(days=1),
        ends_at=NOW + timedelta(days=2),
        priority=99,
    )
    await _add(container, headline="draft", status=BannerStatus.DRAFT, priority=99)
    await _add(container, headline="low", priority=1)
    await _add(container, headline="high", priority=5)

    banner = await container.banners.get_active_banner()()

    assert banner.headline == "high"


async def test_missing_media_falls_back(client: AsyncClient, container: Container) -> None:
    await _add(container, layout=BannerLayout.IMAGE, media_id=uuid.uuid4())
    body = (await client.get("/api/v1/storefront/home-banner")).json()
    assert body["layout"] == "balloons"


@pytest.mark.parametrize("campaigns", [1, 12])
async def test_query_count_is_constant(
    container: Container, query_counter: QueryCounter, campaigns: int
) -> None:
    for i in range(campaigns):
        await _add(container, headline=f"c{i}", priority=i)
    use_case = container.banners.get_active_banner()

    with query_counter.assert_max_queries(1):
        banner = await use_case()

    assert banner.headline == f"c{campaigns - 1}"
