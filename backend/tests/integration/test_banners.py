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
    assert "no-store" in response.headers["cache-control"]


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


# --- admin API -------------------------------------------------------------

ADMIN = "/api/v1/admin/banners"


async def _headers(client: AsyncClient) -> dict[str, str]:
    resp = await client.post("/api/v1/admin/auth/login", json={"password": "admin123"})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['token']}"}


def _body(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "name": "8 Березня 2027",
        "layout": "balloons",
        "starts_at": (NOW - timedelta(days=1)).isoformat(),
        "ends_at": (NOW + timedelta(days=1)).isoformat(),
        "headline": "З 8 Березня!",
        "cta_label": "Обрати",
        "cta_url": "/kulky",
    }
    body.update(overrides)
    return body


async def test_admin_endpoints_require_auth(client: AsyncClient) -> None:
    some_id = uuid.uuid4()
    calls = [
        client.get(ADMIN),
        client.post(ADMIN, json=_body()),
        client.get(f"{ADMIN}/{some_id}"),
        client.patch(f"{ADMIN}/{some_id}", json={"headline": "x"}),
        client.post(f"{ADMIN}/{some_id}/publish"),
        client.post(f"{ADMIN}/{some_id}/unpublish"),
        client.post(f"{ADMIN}/{some_id}/activate"),
        client.post(f"{ADMIN}/{some_id}/deactivate"),
        client.post(f"{ADMIN}/{some_id}/duplicate"),
        client.get(f"{ADMIN}/presets"),
        client.delete(f"{ADMIN}/{some_id}"),
    ]
    for call in calls:
        assert (await call).status_code == 401


async def test_campaign_lifecycle_switches_the_home_banner(client: AsyncClient) -> None:
    headers = await _headers(client)

    created = await client.post(ADMIN, json=_body(), headers=headers)
    assert created.status_code == 201, created.text
    banner = created.json()
    assert banner["state"] == "draft"
    # A draft is invisible to customers.
    home = (await client.get("/api/v1/storefront/home-banner")).json()
    assert home["campaign_id"] is None

    published = await client.post(f"{ADMIN}/{banner['id']}/publish", headers=headers)
    assert published.json()["state"] == "active"
    home = (await client.get("/api/v1/storefront/home-banner")).json()
    assert home["campaign_id"] == banner["id"]
    assert home["headline"] == "З 8 Березня!"

    patched = await client.patch(
        f"{ADMIN}/{banner['id']}", json={"headline": "Нове", "theme": "red"}, headers=headers
    )
    assert patched.json()["headline"] == "Нове"
    assert (await client.get("/api/v1/storefront/home-banner")).json()["theme"] == "red"

    unpublished = await client.post(f"{ADMIN}/{banner['id']}/unpublish", headers=headers)
    assert unpublished.json()["state"] == "draft"
    assert (await client.get("/api/v1/storefront/home-banner")).json()["campaign_id"] is None

    deleted = await client.delete(f"{ADMIN}/{banner['id']}", headers=headers)
    assert deleted.status_code == 204
    assert (await client.get(f"{ADMIN}/{banner['id']}", headers=headers)).status_code == 404


async def test_duplicate_creates_next_year_draft(client: AsyncClient) -> None:
    headers = await _headers(client)
    created = (await client.post(ADMIN, json=_body(), headers=headers)).json()
    copy = await client.post(f"{ADMIN}/{created['id']}/duplicate", headers=headers)
    assert copy.status_code == 201
    body = copy.json()
    assert body["id"] != created["id"]
    assert body["state"] == "draft"
    assert body["name"].endswith("(копія)")
    assert int(body["starts_at"][:4]) == int(created["starts_at"][:4]) + 1


async def test_validation_errors_are_422(client: AsyncClient) -> None:
    headers = await _headers(client)
    ends_before_start = _body(ends_at=(NOW - timedelta(days=5)).isoformat())
    bad_period = await client.post(ADMIN, json=ends_before_start, headers=headers)
    assert bad_period.status_code == 422
    assert bad_period.json()["code"] == "invalid_banner_period"

    no_image = await client.post(ADMIN, json=_body(layout="image"), headers=headers)
    assert no_image.json()["code"] == "banner_image_required"

    unknown_photo = _body(layout="image", media_id=str(uuid.uuid4()))
    missing = await client.post(ADMIN, json=unknown_photo, headers=headers)
    assert missing.json()["code"] == "banner_image_not_found"

    bad_link = await client.post(ADMIN, json=_body(cta_url="javascript:alert(1)"), headers=headers)
    assert bad_link.json()["code"] == "invalid_banner_link"

    no_tag = await client.post(
        ADMIN, json=_body(layout="collection", tag_slug="missing"), headers=headers
    )
    assert no_tag.json()["code"] == "banner_tag_not_found"

    naive_dates = _body(starts_at="2027-03-01T00:00:00")
    assert (await client.post(ADMIN, json=naive_dates, headers=headers)).status_code == 422


@pytest.mark.parametrize("campaigns", [1, 12])
async def test_admin_list_query_count_is_constant(
    client: AsyncClient, container: Container, query_counter: QueryCounter, campaigns: int
) -> None:
    headers = await _headers(client)
    for i in range(campaigns):
        await _add(container, headline=f"c{i}", media_id=uuid.uuid4(), layout=BannerLayout.IMAGE)
    query_counter.reset()

    with query_counter.assert_max_queries(3):  # count + page + one batch media lookup
        response = await client.get(ADMIN, headers=headers)

    assert response.status_code == 200
    assert response.json()["total"] == campaigns


HOME = "/api/v1/storefront/home-banner"
FAR_FUTURE = {
    "starts_at": (NOW + timedelta(days=30)).isoformat(),
    "ends_at": (NOW + timedelta(days=40)).isoformat(),
}


async def test_manual_activation_shows_a_campaign_outside_its_dates(
    client: AsyncClient,
) -> None:
    headers = await _headers(client)
    created = (await client.post(ADMIN, json=_body(**FAR_FUTURE), headers=headers)).json()
    assert created["pinned"] is False
    assert (await client.get(HOME)).json()["campaign_id"] is None

    activated = (await client.post(f"{ADMIN}/{created['id']}/activate", headers=headers)).json()
    assert activated["pinned"] is True
    assert activated["status"] == "published"
    assert activated["state"] == "active"
    assert (await client.get(HOME)).json()["campaign_id"] == created["id"]

    deactivated = (await client.post(f"{ADMIN}/{created['id']}/deactivate", headers=headers)).json()
    assert deactivated["pinned"] is False
    assert deactivated["state"] == "scheduled"
    assert (await client.get(HOME)).json()["campaign_id"] is None


async def test_activating_another_campaign_unpins_the_previous_one(
    client: AsyncClient,
) -> None:
    headers = await _headers(client)
    first = (await client.post(ADMIN, json=_body(**FAR_FUTURE), headers=headers)).json()
    second = (await client.post(ADMIN, json=_body(**FAR_FUTURE), headers=headers)).json()

    await client.post(f"{ADMIN}/{first['id']}/activate", headers=headers)
    await client.post(f"{ADMIN}/{second['id']}/activate", headers=headers)

    first_admin = (await client.get(f"{ADMIN}/{first['id']}", headers=headers)).json()
    assert first_admin["pinned"] is False
    assert (await client.get(HOME)).json()["campaign_id"] == second["id"]


async def test_pinned_campaign_beats_a_scheduled_one(
    client: AsyncClient, container: Container
) -> None:
    scheduled = await _add(container, headline="scheduled", priority=50)
    pinned = await _add(
        container,
        headline="pinned",
        priority=-1,
        starts_at=NOW - timedelta(days=10),
        ends_at=NOW - timedelta(days=5),
    )
    headers = await _headers(client)

    await client.post(f"{ADMIN}/{pinned.id}/activate", headers=headers)

    body = (await client.get(HOME)).json()
    assert body["campaign_id"] == str(pinned.id)
    assert body["headline"] == "pinned"
    assert body["campaign_id"] != str(scheduled.id)


async def test_unpublishing_clears_the_manual_override(client: AsyncClient) -> None:
    headers = await _headers(client)
    created = (await client.post(ADMIN, json=_body(**FAR_FUTURE), headers=headers)).json()
    await client.post(f"{ADMIN}/{created['id']}/activate", headers=headers)

    unpublished = (await client.post(f"{ADMIN}/{created['id']}/unpublish", headers=headers)).json()

    assert unpublished["pinned"] is False
    assert unpublished["state"] == "draft"
    assert (await client.get(HOME)).json()["campaign_id"] is None


async def test_presets_offer_the_four_holidays(client: AsyncClient) -> None:
    headers = await _headers(client)

    response = await client.get(f"{ADMIN}/presets", headers=headers)

    assert response.status_code == 200, response.text
    presets = response.json()
    assert [preset["key"] for preset in presets] == [
        "valentines",
        "march_8",
        "christmas",
        "new_year",
    ]
    for preset in presets:
        assert preset["starts_at"]
        assert preset["ends_at"]
        assert preset["headline"]
        assert preset["cta_url"] == "/kulky"


async def test_a_preset_becomes_a_real_campaign_and_can_be_shown(
    client: AsyncClient,
) -> None:
    headers = await _headers(client)
    preset = (await client.get(f"{ADMIN}/presets", headers=headers)).json()[1]
    payload = {
        key: preset[key]
        for key in (
            "name",
            "layout",
            "starts_at",
            "ends_at",
            "headline",
            "subtitle",
            "priority",
            "cta_label",
            "cta_url",
            "cta2_label",
            "cta2_url",
            "theme",
            "ribbon_text",
            "ribbon_url",
        )
    }

    created = await client.post(ADMIN, json=payload, headers=headers)

    assert created.status_code == 201, created.text
    campaign = created.json()
    assert campaign["name"] == preset["name"]
    await client.post(f"{ADMIN}/{campaign['id']}/activate", headers=headers)
    home = (await client.get(HOME)).json()
    assert home["campaign_id"] == campaign["id"]
    assert home["headline"] == preset["headline"]
    assert home["ribbon_text"] == preset["ribbon_text"]


async def test_only_one_campaign_can_stay_pinned(container: Container) -> None:
    from sqlalchemy.exc import IntegrityError

    await _add(container, pinned=True)
    with pytest.raises(IntegrityError):
        await _add(container, pinned=True)


async def test_collection_banner_accepts_an_existing_tag(client: AsyncClient) -> None:
    headers = await _headers(client)
    tag = await client.post(
        "/api/v1/catalog/tags",
        json={"group": "occasion", "name": "8 Березня", "slug": "8-bereznia"},
        headers=headers,
    )
    assert tag.status_code == 201, tag.text

    created = await client.post(
        ADMIN, json=_body(layout="collection", tag_slug="8-bereznia"), headers=headers
    )

    assert created.status_code == 201, created.text
    assert created.json()["tag_slug"] == "8-bereznia"
