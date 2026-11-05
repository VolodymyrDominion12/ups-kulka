import uuid
from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ups_kulka.modules.banners.domain.entities import (
    BannerCampaign,
    BannerLayout,
    BannerStatus,
    BannerTheme,
)
from ups_kulka.modules.banners.domain.errors import BannerNotFound
from ups_kulka.modules.banners.infrastructure.tables import BannerCampaignRow
from ups_kulka.shared.application.pagination import Page, PageRequest


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


def _apply(row: BannerCampaignRow, campaign: BannerCampaign) -> None:
    row.name = campaign.name
    row.layout = campaign.layout.value
    row.status = campaign.status.value
    row.starts_at = campaign.starts_at
    row.ends_at = campaign.ends_at
    row.priority = campaign.priority
    row.headline = campaign.headline
    row.subtitle = campaign.subtitle
    row.cta_label = campaign.cta_label
    row.cta_url = campaign.cta_url
    row.cta2_label = campaign.cta2_label
    row.cta2_url = campaign.cta2_url
    row.media_id = campaign.media_id
    row.media_mobile_id = campaign.media_mobile_id
    row.image_alt = campaign.image_alt
    row.theme = campaign.theme.value
    row.tag_slug = campaign.tag_slug
    row.ribbon_text = campaign.ribbon_text
    row.ribbon_url = campaign.ribbon_url
    row.created_at = campaign.created_at
    row.updated_at = campaign.updated_at


class SqlAlchemyBannerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, campaign: BannerCampaign) -> None:
        row = BannerCampaignRow(id=campaign.id)
        _apply(row, campaign)
        self._session.add(row)
        await self._session.flush()

    async def get(self, campaign_id: uuid.UUID) -> BannerCampaign | None:
        row = await self._session.get(BannerCampaignRow, campaign_id)
        return campaign_to_domain(row) if row else None

    async def list_page(self, page: PageRequest) -> Page[BannerCampaign]:
        total = await self._session.scalar(select(func.count()).select_from(BannerCampaignRow))
        rows = await self._session.scalars(
            select(BannerCampaignRow)
            .order_by(BannerCampaignRow.starts_at.desc(), BannerCampaignRow.id.desc())
            .limit(page.limit)
            .offset(page.offset)
        )
        return Page(
            items=tuple(campaign_to_domain(row) for row in rows),
            total=total or 0,
            limit=page.limit,
            offset=page.offset,
        )

    async def update(self, campaign: BannerCampaign) -> None:
        row = await self._session.get(BannerCampaignRow, campaign.id)
        if row is None:
            raise BannerNotFound
        _apply(row, campaign)
        await self._session.flush()

    async def delete(self, campaign_id: uuid.UUID) -> bool:
        result = await self._session.execute(
            delete(BannerCampaignRow).where(BannerCampaignRow.id == campaign_id)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]  # CursorResult has rowcount

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
