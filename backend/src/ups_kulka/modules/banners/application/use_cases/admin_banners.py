"""Admin use cases for home banner campaigns (specs/017-home-banners)."""

import uuid
from collections.abc import Callable, Sequence
from datetime import datetime

from ups_kulka.modules.banners.application.dto import (
    AdminBannerDTO,
    BannerIdCommand,
    CreateBannerCommand,
    ListBannersQuery,
    UpdateBannerCommand,
)
from ups_kulka.modules.banners.application.ports import (
    AdminGuard,
    BannerUnitOfWork,
    BannerUnitOfWorkFactory,
    MediaLookup,
    TagLookup,
)
from ups_kulka.modules.banners.application.use_cases.get_active_banner import utc_now
from ups_kulka.modules.banners.domain.entities import (
    BannerCampaign,
    BannerLayout,
    BannerStatus,
    BannerTheme,
)
from ups_kulka.modules.banners.domain.errors import (
    BannerImageNotFound,
    BannerNotFound,
    BannerTagNotFound,
)
from ups_kulka.shared.application.pagination import Page, PageRequest

COPY_SUFFIX = " (копія)"


async def _to_dtos(
    campaigns: Sequence[BannerCampaign], media: MediaLookup, now: datetime
) -> list[AdminBannerDTO]:
    """One batch media lookup for the whole list (no N+1)."""
    ids = {mid for c in campaigns for mid in (c.media_id, c.media_mobile_id) if mid}
    images = await media.get_images(list(ids)) if ids else {}
    return [AdminBannerDTO.from_campaign(c, c.state_at(now), images) for c in campaigns]


async def _check_references(campaign: BannerCampaign, media: MediaLookup, tags: TagLookup) -> None:
    """Photos and tag must exist: reference other modules through their public facades."""
    media_ids = [mid for mid in (campaign.media_id, campaign.media_mobile_id) if mid]
    if media_ids and len(await media.get_images(media_ids)) != len(set(media_ids)):
        raise BannerImageNotFound
    slug = campaign.tag_slug
    if campaign.layout is not BannerLayout.COLLECTION or not slug:
        return
    if slug not in await tags.existing_slugs([slug]):
        raise BannerTagNotFound(slug)


async def _load(uow: BannerUnitOfWork, campaign_id: uuid.UUID) -> BannerCampaign:
    campaign = await uow.banners.get(campaign_id)
    if campaign is None:
        raise BannerNotFound
    return campaign


class _AdminUseCase:
    def __init__(
        self,
        uow_factory: BannerUnitOfWorkFactory,
        media: MediaLookup,
        auth: AdminGuard | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._uow_factory = uow_factory
        self._media = media
        self._auth = auth
        self._clock = clock

    def _require_admin(self, token: str | None) -> None:
        if self._auth is not None:
            self._auth.require_admin(token)

    async def _dto(self, campaign: BannerCampaign) -> AdminBannerDTO:
        return (await _to_dtos([campaign], self._media, self._clock()))[0]


class ListBanners(_AdminUseCase):
    async def __call__(self, query: ListBannersQuery) -> Page[AdminBannerDTO]:
        self._require_admin(query.auth_token)
        async with self._uow_factory() as uow:
            page = await uow.banners.list_page(PageRequest(limit=query.limit, offset=query.offset))
        items = await _to_dtos(page.items, self._media, self._clock())
        return Page(items=tuple(items), total=page.total, limit=page.limit, offset=page.offset)


class GetBanner(_AdminUseCase):
    async def __call__(self, cmd: BannerIdCommand) -> AdminBannerDTO:
        self._require_admin(cmd.auth_token)
        async with self._uow_factory() as uow:
            campaign = await _load(uow, cmd.campaign_id)
        return await self._dto(campaign)


class _ReferenceCheckingUseCase(_AdminUseCase):
    def __init__(
        self,
        uow_factory: BannerUnitOfWorkFactory,
        media: MediaLookup,
        tags: TagLookup,
        auth: AdminGuard | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        super().__init__(uow_factory, media, auth, clock)
        self._tags = tags


class CreateBanner(_ReferenceCheckingUseCase):
    async def __call__(self, cmd: CreateBannerCommand) -> AdminBannerDTO:
        self._require_admin(cmd.auth_token)
        campaign = BannerCampaign.create(
            name=cmd.name,
            layout=BannerLayout(cmd.layout),
            starts_at=cmd.starts_at,
            ends_at=cmd.ends_at,
            headline=cmd.headline,
            subtitle=cmd.subtitle,
            priority=cmd.priority,
            cta_label=cmd.cta_label,
            cta_url=cmd.cta_url,
            cta2_label=cmd.cta2_label,
            cta2_url=cmd.cta2_url,
            media_id=cmd.media_id,
            media_mobile_id=cmd.media_mobile_id,
            image_alt=cmd.image_alt,
            theme=BannerTheme(cmd.theme),
            tag_slug=cmd.tag_slug,
            ribbon_text=cmd.ribbon_text,
            ribbon_url=cmd.ribbon_url,
        )
        await _check_references(campaign, self._media, self._tags)
        async with self._uow_factory() as uow:
            await uow.banners.add(campaign)
            await uow.commit()
        return await self._dto(campaign)


class UpdateBanner(_ReferenceCheckingUseCase):
    async def __call__(self, cmd: UpdateBannerCommand) -> AdminBannerDTO:
        self._require_admin(cmd.auth_token)
        changes = dict(cmd.changes)
        if "layout" in changes:
            changes["layout"] = BannerLayout(changes["layout"])
        if "theme" in changes:
            changes["theme"] = BannerTheme(changes["theme"])
        async with self._uow_factory() as uow:
            current = await _load(uow, cmd.campaign_id)
            campaign = current.revise(**changes)
            await _check_references(campaign, self._media, self._tags)
            await uow.banners.update(campaign)
            await uow.commit()
        return await self._dto(campaign)


class SetBannerPublished(_AdminUseCase):
    def __init__(
        self,
        uow_factory: BannerUnitOfWorkFactory,
        media: MediaLookup,
        published: bool,
        auth: AdminGuard | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        super().__init__(uow_factory, media, auth, clock)
        self._status = BannerStatus.PUBLISHED if published else BannerStatus.DRAFT

    async def __call__(self, cmd: BannerIdCommand) -> AdminBannerDTO:
        self._require_admin(cmd.auth_token)
        publishing = self._status is BannerStatus.PUBLISHED
        async with self._uow_factory() as uow:
            current = await _load(uow, cmd.campaign_id)
            # Taking a campaign off the site also removes its manual override.
            campaign = current.revise(status=self._status, pinned=current.pinned and publishing)
            await uow.banners.update(campaign)
            await uow.commit()
        return await self._dto(campaign)


class SetBannerPinned(_AdminUseCase):
    """Show a campaign right now, ignoring its dates, or stop the manual override."""

    def __init__(
        self,
        uow_factory: BannerUnitOfWorkFactory,
        media: MediaLookup,
        pinned: bool,
        auth: AdminGuard | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        super().__init__(uow_factory, media, auth, clock)
        self._pinned = pinned

    async def __call__(self, cmd: BannerIdCommand) -> AdminBannerDTO:
        self._require_admin(cmd.auth_token)
        async with self._uow_factory() as uow:
            current = await _load(uow, cmd.campaign_id)
            if self._pinned:
                await uow.banners.clear_pinned(keep_id=current.id)
                campaign = current.activate_now()
            else:
                campaign = current.deactivate_now()
            await uow.banners.update(campaign)
            await uow.commit()
        return await self._dto(campaign)


class DuplicateBanner(_AdminUseCase):
    async def __call__(self, cmd: BannerIdCommand) -> AdminBannerDTO:
        self._require_admin(cmd.auth_token)
        async with self._uow_factory() as uow:
            source = await _load(uow, cmd.campaign_id)
            copy = source.duplicate(f"{source.name[: 120 - len(COPY_SUFFIX)]}{COPY_SUFFIX}")
            await uow.banners.add(copy)
            await uow.commit()
        return await self._dto(copy)


class DeleteBanner(_AdminUseCase):
    async def __call__(self, cmd: BannerIdCommand) -> None:
        self._require_admin(cmd.auth_token)
        async with self._uow_factory() as uow:
            if not await uow.banners.delete(cmd.campaign_id):
                raise BannerNotFound
            await uow.commit()
