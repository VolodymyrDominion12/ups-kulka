import uuid
from dataclasses import dataclass, fields, replace
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from ups_kulka.modules.banners.domain.errors import (
    BannerImageRequired,
    BannerTagRequired,
    InvalidBannerLink,
    InvalidBannerPeriod,
    InvalidBannerText,
)

MAX_NAME_LENGTH = 120
MAX_HEADLINE_LENGTH = 120
MAX_SUBTITLE_LENGTH = 300
MAX_LABEL_LENGTH = 40
MAX_URL_LENGTH = 255


class BannerLayout(StrEnum):
    BALLOONS = "balloons"
    IMAGE = "image"
    SPLIT = "split"
    COLLECTION = "collection"


class BannerStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class BannerTheme(StrEnum):
    ROSE = "rose"
    RED = "red"
    GOLD = "gold"
    DARK = "dark"


class BannerState(StrEnum):
    """Where a campaign is in its life, as the admin sees it."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    EXPIRED = "expired"


IMAGE_LAYOUTS = frozenset({BannerLayout.IMAGE, BannerLayout.SPLIT})


def shift_one_year(moment: datetime) -> datetime:
    """Same calendar date next year (holidays are fixed dates); 29 Feb becomes 28 Feb."""
    try:
        return moment.replace(year=moment.year + 1)
    except ValueError:
        return moment.replace(year=moment.year + 1, day=28)


def is_safe_link(url: str) -> bool:
    """Relative path (but not protocol-relative `//host`) or an https URL."""
    if len(url) > MAX_URL_LENGTH:
        return False
    if url.startswith("/"):
        return not url.startswith("//")
    return url.startswith("https://")


@dataclass(frozen=True, slots=True)
class BannerCampaign:
    id: uuid.UUID
    name: str
    layout: BannerLayout
    status: BannerStatus
    pinned: bool
    starts_at: datetime
    ends_at: datetime
    priority: int
    headline: str
    subtitle: str
    cta_label: str
    cta_url: str
    cta2_label: str
    cta2_url: str
    media_id: uuid.UUID | None
    media_mobile_id: uuid.UUID | None
    image_alt: str
    theme: BannerTheme
    tag_slug: str | None
    ribbon_text: str
    ribbon_url: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        name: str,
        layout: BannerLayout,
        starts_at: datetime,
        ends_at: datetime,
        headline: str,
        subtitle: str = "",
        status: BannerStatus = BannerStatus.DRAFT,
        pinned: bool = False,
        priority: int = 0,
        cta_label: str = "",
        cta_url: str = "",
        cta2_label: str = "",
        cta2_url: str = "",
        media_id: uuid.UUID | None = None,
        media_mobile_id: uuid.UUID | None = None,
        image_alt: str = "",
        theme: BannerTheme = BannerTheme.ROSE,
        tag_slug: str | None = None,
        ribbon_text: str = "",
        ribbon_url: str = "",
        campaign_id: uuid.UUID | None = None,
    ) -> "BannerCampaign":
        clean_name = name.strip()
        clean_headline = headline.strip()
        clean_subtitle = subtitle.strip()
        if not clean_name or not clean_headline:
            raise InvalidBannerText
        if (
            len(clean_name) > MAX_NAME_LENGTH
            or len(clean_headline) > MAX_HEADLINE_LENGTH
            or len(clean_subtitle) > MAX_SUBTITLE_LENGTH
        ):
            raise InvalidBannerText("Занадто довгий текст банера")
        if ends_at <= starts_at:
            raise InvalidBannerPeriod
        if layout in IMAGE_LAYOUTS and media_id is None:
            raise BannerImageRequired
        if layout is BannerLayout.COLLECTION and not tag_slug:
            raise BannerTagRequired

        for label, url in ((cta_label, cta_url), (cta2_label, cta2_url)):
            if bool(label.strip()) != bool(url.strip()):
                raise InvalidBannerLink
            if len(label.strip()) > MAX_LABEL_LENGTH:
                raise InvalidBannerText("Занадто довгий напис на кнопці")
        for url in (cta_url, cta2_url, ribbon_url):
            if url and not is_safe_link(url.strip()):
                raise InvalidBannerLink

        now = datetime.now(UTC)
        return cls(
            id=campaign_id or uuid.uuid4(),
            name=clean_name,
            layout=layout,
            status=status,
            pinned=pinned,
            starts_at=starts_at,
            ends_at=ends_at,
            priority=priority,
            headline=clean_headline,
            subtitle=clean_subtitle,
            cta_label=cta_label.strip(),
            cta_url=cta_url.strip(),
            cta2_label=cta2_label.strip(),
            cta2_url=cta2_url.strip(),
            media_id=media_id,
            media_mobile_id=media_mobile_id,
            image_alt=image_alt.strip(),
            theme=theme,
            tag_slug=tag_slug,
            ribbon_text=ribbon_text.strip(),
            ribbon_url=ribbon_url.strip(),
            created_at=now,
            updated_at=now,
        )

    def is_active_at(self, moment: datetime) -> bool:
        """On the storefront right now: pinned manually, or published inside its period."""
        if self.status is not BannerStatus.PUBLISHED:
            return False
        return self.pinned or self.starts_at <= moment < self.ends_at

    def state_at(self, moment: datetime) -> BannerState:
        if self.status is BannerStatus.DRAFT:
            return BannerState.DRAFT
        if self.pinned:
            return BannerState.ACTIVE
        if moment < self.starts_at:
            return BannerState.SCHEDULED
        if moment >= self.ends_at:
            return BannerState.EXPIRED
        return BannerState.ACTIVE

    def activate_now(self) -> "BannerCampaign":
        """Show on the site right now, ignoring the schedule (drafts become published)."""
        return self.revise(status=BannerStatus.PUBLISHED, pinned=True)

    def deactivate_now(self) -> "BannerCampaign":
        """Drop the manual override: the campaign lives by its schedule again."""
        return self.revise(pinned=False)

    def revise(self, **changes: Any) -> "BannerCampaign":
        """A copy with ``changes`` applied, validated by the same rules as ``create``."""
        values: dict[str, Any] = {  # Any: heterogeneous field values, validated in ``create``
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.name not in {"id", "created_at", "updated_at"}
        }
        unknown = set(changes) - set(values)
        if unknown:
            raise ValueError(f"Unknown banner fields: {sorted(unknown)}")
        values.update(changes)
        revised = BannerCampaign.create(campaign_id=self.id, **values)
        return replace(revised, created_at=self.created_at)

    def duplicate(self, name: str) -> "BannerCampaign":
        """Next year's copy: a draft with the same content and the dates moved one year ahead."""
        copy = self.revise(
            name=name,
            status=BannerStatus.DRAFT,
            pinned=False,
            starts_at=shift_one_year(self.starts_at),
            ends_at=shift_one_year(self.ends_at),
        )
        return replace(copy, id=uuid.uuid4())
