from dataclasses import dataclass

from ups_kulka.modules.banners.domain.entities import BannerCampaign, BannerLayout, BannerTheme


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
