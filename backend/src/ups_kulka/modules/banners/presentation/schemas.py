import uuid
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict

from ups_kulka.modules.banners.application.dto import (
    AdminBannerDTO,
    BannerImageDTO,
    CreateBannerCommand,
    HomeBannerDTO,
    UpdateBannerCommand,
)
from ups_kulka.shared.application.pagination import Page

LayoutName = Literal["balloons", "image", "split", "collection"]
ThemeName = Literal["rose", "red", "gold", "dark"]


class BannerImageOut(BaseModel):
    url_prefix: str
    blur_data_url: str
    width: int
    height: int
    variants: dict[str, str]

    @classmethod
    def from_dto(cls, dto: BannerImageDTO) -> "BannerImageOut":
        return cls(
            url_prefix=dto.url_prefix,
            blur_data_url=dto.blur_data_url,
            width=dto.width,
            height=dto.height,
            variants=dto.variants,
        )


class HomeBannerOut(BaseModel):
    layout: str
    campaign_id: str | None
    theme: str
    headline: str
    subtitle: str
    cta_label: str
    cta_url: str
    cta2_label: str
    cta2_url: str
    image: BannerImageOut | None
    image_mobile: BannerImageOut | None
    image_alt: str
    tag_slug: str | None
    ribbon_text: str
    ribbon_url: str

    @classmethod
    def from_dto(cls, dto: HomeBannerDTO) -> "HomeBannerOut":
        return cls(
            layout=dto.layout.value,
            campaign_id=dto.campaign_id,
            theme=dto.theme.value,
            headline=dto.headline,
            subtitle=dto.subtitle,
            cta_label=dto.cta_label,
            cta_url=dto.cta_url,
            cta2_label=dto.cta2_label,
            cta2_url=dto.cta2_url,
            image=BannerImageOut.from_dto(dto.image) if dto.image else None,
            image_mobile=BannerImageOut.from_dto(dto.image_mobile) if dto.image_mobile else None,
            image_alt=dto.image_alt,
            tag_slug=dto.tag_slug,
            ribbon_text=dto.ribbon_text,
            ribbon_url=dto.ribbon_url,
        )


class AdminBannerOut(BaseModel):
    id: uuid.UUID
    name: str
    layout: str
    status: str
    state: str
    starts_at: AwareDatetime
    ends_at: AwareDatetime
    priority: int
    headline: str
    subtitle: str
    cta_label: str
    cta_url: str
    cta2_label: str
    cta2_url: str
    media_id: uuid.UUID | None
    media_mobile_id: uuid.UUID | None
    image: BannerImageOut | None
    image_mobile: BannerImageOut | None
    image_alt: str
    theme: str
    tag_slug: str | None
    ribbon_text: str
    ribbon_url: str
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @classmethod
    def from_dto(cls, dto: AdminBannerDTO) -> "AdminBannerOut":
        return cls(
            id=dto.id,
            name=dto.name,
            layout=dto.layout.value,
            status=dto.status,
            state=dto.state.value,
            starts_at=dto.starts_at,
            ends_at=dto.ends_at,
            priority=dto.priority,
            headline=dto.headline,
            subtitle=dto.subtitle,
            cta_label=dto.cta_label,
            cta_url=dto.cta_url,
            cta2_label=dto.cta2_label,
            cta2_url=dto.cta2_url,
            media_id=dto.media_id,
            media_mobile_id=dto.media_mobile_id,
            image=BannerImageOut.from_dto(dto.image) if dto.image else None,
            image_mobile=BannerImageOut.from_dto(dto.image_mobile) if dto.image_mobile else None,
            image_alt=dto.image_alt,
            theme=dto.theme.value,
            tag_slug=dto.tag_slug,
            ribbon_text=dto.ribbon_text,
            ribbon_url=dto.ribbon_url,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )


class AdminBannerPageOut(BaseModel):
    items: list[AdminBannerOut]
    total: int
    limit: int
    offset: int

    @classmethod
    def from_page(cls, page: Page[AdminBannerDTO]) -> "AdminBannerPageOut":
        return cls(
            items=[AdminBannerOut.from_dto(item) for item in page.items],
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )


class BannerCreateIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    layout: LayoutName
    starts_at: AwareDatetime
    ends_at: AwareDatetime
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
    theme: ThemeName = "rose"
    tag_slug: str | None = None
    ribbon_text: str = ""
    ribbon_url: str = ""

    def to_command(self, auth_token: str | None) -> CreateBannerCommand:
        return CreateBannerCommand(**self.model_dump(), auth_token=auth_token)


class BannerUpdateIn(BaseModel):
    """PATCH body: only the fields that are sent change (null clears optional ones)."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    layout: LayoutName | None = None
    starts_at: AwareDatetime | None = None
    ends_at: AwareDatetime | None = None
    headline: str | None = None
    subtitle: str | None = None
    priority: int | None = None
    cta_label: str | None = None
    cta_url: str | None = None
    cta2_label: str | None = None
    cta2_url: str | None = None
    media_id: uuid.UUID | None = None
    media_mobile_id: uuid.UUID | None = None
    image_alt: str | None = None
    theme: ThemeName | None = None
    tag_slug: str | None = None
    ribbon_text: str | None = None
    ribbon_url: str | None = None

    def to_command(self, campaign_id: uuid.UUID, auth_token: str | None) -> UpdateBannerCommand:
        sent = self.model_dump(exclude_unset=True)
        nullable = {"media_id", "media_mobile_id", "tag_slug"}
        changes = {k: v for k, v in sent.items() if v is not None or k in nullable}
        return UpdateBannerCommand(campaign_id=campaign_id, changes=changes, auth_token=auth_token)
