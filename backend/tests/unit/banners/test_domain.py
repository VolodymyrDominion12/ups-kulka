import uuid
from datetime import UTC, datetime, timedelta

import pytest

from ups_kulka.modules.banners.domain.entities import (
    BannerCampaign,
    BannerLayout,
    BannerStatus,
    is_safe_link,
)
from ups_kulka.modules.banners.domain.errors import (
    BannerImageRequired,
    BannerTagRequired,
    InvalidBannerLink,
    InvalidBannerPeriod,
    InvalidBannerText,
)

START = datetime(2027, 3, 1, tzinfo=UTC)
END = datetime(2027, 3, 9, tzinfo=UTC)


def make(**overrides: object) -> BannerCampaign:
    params: dict[str, object] = {
        "name": "8 Березня 2027",
        "layout": BannerLayout.BALLOONS,
        "starts_at": START,
        "ends_at": END,
        "headline": "З 8 Березня!",
    }
    params.update(overrides)
    return BannerCampaign.create(**params)  # type: ignore[arg-type]


def test_create_defaults_to_draft() -> None:
    campaign = make()
    assert campaign.status is BannerStatus.DRAFT
    assert campaign.priority == 0


def test_period_must_be_positive() -> None:
    with pytest.raises(InvalidBannerPeriod):
        make(ends_at=START)


@pytest.mark.parametrize("layout", [BannerLayout.IMAGE, BannerLayout.SPLIT])
def test_image_layouts_require_image(layout: BannerLayout) -> None:
    with pytest.raises(BannerImageRequired):
        make(layout=layout)
    assert make(layout=layout, media_id=uuid.uuid4()).media_id is not None


def test_collection_requires_tag() -> None:
    with pytest.raises(BannerTagRequired):
        make(layout=BannerLayout.COLLECTION)
    assert make(layout=BannerLayout.COLLECTION, tag_slug="8-bereznia").tag_slug == "8-bereznia"


@pytest.mark.parametrize("name", ["", "   "])
def test_name_and_headline_required(name: str) -> None:
    with pytest.raises(InvalidBannerText):
        make(name=name)
    with pytest.raises(InvalidBannerText):
        make(headline=name)


def test_too_long_headline_rejected() -> None:
    with pytest.raises(InvalidBannerText):
        make(headline="x" * 121)


@pytest.mark.parametrize(
    ("url", "ok"),
    [
        ("/kulky", True),
        ("/kulky?tag=8-bereznia", True),
        ("https://instagram.com/x", True),
        ("//evil.example", False),
        ("http://insecure.example", False),
        ("javascript:alert(1)", False),
        ("kulky", False),
        ("/" + "a" * 300, False),
    ],
)
def test_safe_link(url: str, ok: bool) -> None:
    assert is_safe_link(url) is ok


def test_cta_needs_label_and_url_together() -> None:
    with pytest.raises(InvalidBannerLink):
        make(cta_label="Обрати")
    with pytest.raises(InvalidBannerLink):
        make(cta_url="/kulky")
    with pytest.raises(InvalidBannerLink):
        make(cta_label="Обрати", cta_url="javascript:alert(1)")
    with pytest.raises(InvalidBannerLink):
        make(ribbon_text="Акція", ribbon_url="//evil.example")
    assert make(cta_label="Обрати", cta_url="/kulky").cta_url == "/kulky"


def test_is_active_at_boundaries() -> None:
    published = make(status=BannerStatus.PUBLISHED)
    assert published.is_active_at(START)
    assert published.is_active_at(END - timedelta(seconds=1))
    assert not published.is_active_at(END)
    assert not published.is_active_at(START - timedelta(seconds=1))
    assert not make().is_active_at(START)  # draft
