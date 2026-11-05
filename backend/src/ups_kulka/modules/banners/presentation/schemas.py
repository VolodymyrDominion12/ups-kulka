from pydantic import BaseModel

from ups_kulka.modules.banners.application.dto import BannerImageDTO, HomeBannerDTO


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
