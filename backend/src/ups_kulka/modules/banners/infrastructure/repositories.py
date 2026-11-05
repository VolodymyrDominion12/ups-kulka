from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ups_kulka.modules.banners.domain.entities import (
    BannerCampaign,
    BannerLayout,
    BannerStatus,
    BannerTheme,
)
from ups_kulka.modules.banners.infrastructure.tables import BannerCampaignRow


def campaign_to_domain(row: BannerCampaignRow) -> BannerCampaign:
    return BannerCampaign(
        id=row.id,
        name=row.name,
        layout=BannerLayout(row.layout),
        status=BannerStatus(row.status),
        starts_at=row.starts_at,
        ends_at=row.ends_at,
        priority=row.priority,
        headline=row.headline,
        subtitle=row.subtitle,
        cta_label=row.cta_label,
        cta_url=row.cta_url,
        cta2_label=row.cta2_label,
        cta2_url=row.cta2_url,
        media_id=row.media_id,
        media_mobile_id=row.media_mobile_id,
        image_alt=row.image_alt,
        theme=BannerTheme(row.theme),
        tag_slug=row.tag_slug,
        ribbon_text=row.ribbon_text,
        ribbon_url=row.ribbon_url,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class SqlAlchemyBannerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, campaign: BannerCampaign) -> None:
        self._session.add(
            BannerCampaignRow(
                id=campaign.id,
                name=campaign.name,
                layout=campaign.layout.value,
                status=campaign.status.value,
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
                image_alt=campaign.image_alt,
                theme=campaign.theme.value,
                tag_slug=campaign.tag_slug,
                ribbon_text=campaign.ribbon_text,
                ribbon_url=campaign.ribbon_url,
                created_at=campaign.created_at,
                updated_at=campaign.updated_at,
            )
        )
        await self._session.flush()

    async def get_active(self, now: datetime) -> BannerCampaign | None:
        row = await self._session.scalar(
            select(BannerCampaignRow)
            .where(
                BannerCampaignRow.status == BannerStatus.PUBLISHED.value,
                BannerCampaignRow.starts_at <= now,
                BannerCampaignRow.ends_at > now,
            )
            .order_by(BannerCampaignRow.priority.desc(), BannerCampaignRow.starts_at.desc())
            .limit(1)
        )
        return campaign_to_domain(row) if row else None
