import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ups_kulka.modules.banners.domain.entities import (
    BannerCampaign,
    BannerLayout,
    BannerState,
    BannerTheme,
)


@dataclass(frozen=True, slots=True)
class BannerImageDTO:
    url_prefix: str
    blur_data_url: str
    width: int
    height: int
    variants: dict[str, str]


@dataclass(frozen=True, slots=True)
class HomeBannerDTO:
    """What the storefront needs to draw the home hero.

    ``campaign_id is None`` means "no active campaign": draw the default balloons hero.
    """

    layout: BannerLayout
    campaign_id: str | None = None
    theme: BannerTheme = BannerTheme.ROSE
    headline: str = ""
    subtitle: str = ""
    cta_label: str = ""
    cta_url: str = ""
    cta2_label: str = ""
    cta2_url: str = ""
    image: BannerImageDTO | None = None
    image_mobile: BannerImageDTO | None = None
    image_alt: str = ""
    tag_slug: str | None = None
    ribbon_text: str = ""
    ribbon_url: str = ""

    @classmethod
    def default(cls) -> "HomeBannerDTO":
        return cls(layout=BannerLayout.BALLOONS)

    @classmethod
    def from_campaign(
        cls,
        campaign: BannerCampaign,
        image: BannerImageDTO | None,
        image_mobile: BannerImageDTO | None,
    ) -> "HomeBannerDTO":
        return cls(
            layout=campaign.layout,
            campaign_id=str(campaign.id),
            theme=campaign.theme,
            headline=campaign.headline,
            subtitle=campaign.subtitle,
            cta_label=campaign.cta_label,
            cta_url=campaign.cta_url,
            cta2_label=campaign.cta2_label,
            cta2_url=campaign.cta2_url,
            image=image,
            image_mobile=image_mobile,
            image_alt=campaign.image_alt,
            tag_slug=campaign.tag_slug,
            ribbon_text=campaign.ribbon_text,
            ribbon_url=campaign.ribbon_url,
        )


@dataclass(frozen=True, slots=True)
class AdminBannerDTO:
    id: uuid.UUID
    name: str
    layout: BannerLayout
    status: str
    state: BannerState
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
    image: BannerImageDTO | None
    image_mobile: BannerImageDTO | None
    image_alt: str
    theme: BannerTheme
    tag_slug: str | None
    ribbon_text: str
    ribbon_url: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_campaign(
        cls,
        campaign: BannerCampaign,
        state: BannerState,
        images: Mapping[uuid.UUID, BannerImageDTO],
    ) -> "AdminBannerDTO":
        return cls(
            id=campaign.id,
            name=campaign.name,
            layout=campaign.layout,
            status=campaign.status.value,
            state=state,
            starts_at=campaign.starts_at,
            ends_at=campaign.ends_at,
            priority=campaign.priority,
            headline=campaign.headline,
            subtitle=campaign.subtitle,
            cta_label=campaign.cta_label,
            cta_url=campaign.cta_url,
            cta2_label=campaign.cta2_label,
            cta2_url=campaign.cta2_url,
            media_id=campaign.media_id,
            media_mobile_id=campaign.media_mobile_id,
            image=images.get(campaign.media_id) if campaign.media_id else None,
            image_mobile=images.get(campaign.media_mobile_id) if campaign.media_mobile_id else None,
            image_alt=campaign.image_alt,
            theme=campaign.theme,
            tag_slug=campaign.tag_slug,
            ribbon_text=campaign.ribbon_text,
            ribbon_url=campaign.ribbon_url,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
        )


@dataclass(frozen=True, slots=True)
class CreateBannerCommand:
    name: str
    layout: str
    starts_at: datetime
    ends_at: datetime
    headline: str
    subtitle: str = ""
    priority: int = 0
    cta_label: str = ""
    cta_url: str = ""
    cta2_label: str = ""
    cta2_url: str = ""
    media_id: uuid.UUID | None = None
    media_mobile_id: uuid.UUID | None = None
    image_alt: str = ""
    theme: str = "rose"
    tag_slug: str | None = None
    ribbon_text: str = ""
    ribbon_url: str = ""
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateBannerCommand:
    campaign_id: uuid.UUID
    # Only the fields the admin sent (PATCH); values are validated by the domain.
    changes: Mapping[str, Any]  # Any: heterogeneous field values
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class BannerIdCommand:
    campaign_id: uuid.UUID
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class ListBannersQuery:
    limit: int = 50
    offset: int = 0
    auth_token: str | None = None
