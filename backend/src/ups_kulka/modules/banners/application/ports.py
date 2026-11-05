import uuid
from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Protocol

from ups_kulka.modules.banners.application.dto import BannerImageDTO
from ups_kulka.modules.banners.domain.entities import BannerCampaign
from ups_kulka.shared.application.pagination import Page, PageRequest
from ups_kulka.shared.application.uow import UnitOfWork


class AdminGuard(Protocol):
    def require_admin(self, token: str | None) -> None: ...


class TagLookup(Protocol):
    async def existing_slugs(self, slugs: Sequence[str]) -> set[str]:
        """Which tag slugs exist, via the catalog module's public facade."""
        ...


class BannerRepository(Protocol):
    async def add(self, campaign: BannerCampaign) -> None: ...

    async def get_active(self, now: datetime) -> BannerCampaign | None:
        """Published campaign covering ``now`` with the highest priority, in ONE query."""
        ...

    async def get(self, campaign_id: uuid.UUID) -> BannerCampaign | None: ...

    async def list_page(self, page: PageRequest) -> Page[BannerCampaign]:
        """Newest period first; ``total`` plus one page query."""
        ...

    async def update(self, campaign: BannerCampaign) -> None: ...

    async def delete(self, campaign_id: uuid.UUID) -> bool: ...


class BannerUnitOfWork(UnitOfWork, Protocol):
    banners: BannerRepository


type BannerUnitOfWorkFactory = Callable[[], BannerUnitOfWork]


class MediaLookup(Protocol):
    async def get_images(self, ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, BannerImageDTO]:
        """Batch lookup via the media module's public facade."""
        ...
