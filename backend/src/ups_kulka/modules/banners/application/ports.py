import uuid
from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Protocol

from ups_kulka.modules.banners.application.dto import BannerImageDTO
from ups_kulka.modules.banners.domain.entities import BannerCampaign
from ups_kulka.shared.application.uow import UnitOfWork


class BannerRepository(Protocol):
    async def add(self, campaign: BannerCampaign) -> None: ...

    async def get_active(self, now: datetime) -> BannerCampaign | None:
        """Published campaign covering ``now`` with the highest priority, in ONE query."""
        ...


class BannerUnitOfWork(UnitOfWork, Protocol):
    banners: BannerRepository


type BannerUnitOfWorkFactory = Callable[[], BannerUnitOfWork]


class MediaLookup(Protocol):
    async def get_images(self, ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, BannerImageDTO]:
        """Batch lookup via the media module's public facade."""
        ...
