"""In-memory fakes of banners ports for fast unit tests (no DB)."""

import uuid
from collections.abc import Sequence
from datetime import datetime
from types import TracebackType
from typing import Self

from ups_kulka.modules.banners.application.dto import BannerImageDTO
from ups_kulka.modules.banners.domain.entities import BannerCampaign
from ups_kulka.shared.application.pagination import Page, PageRequest

IMAGE = BannerImageDTO(
    url_prefix="/media/x", blur_data_url="data:", width=1600, height=800, variants={}
)


class InMemoryBannerRepository:
    def __init__(self, store: dict[uuid.UUID, BannerCampaign]) -> None:
        self._store = store

    async def add(self, campaign: BannerCampaign) -> None:
        self._store[campaign.id] = campaign

    async def get(self, campaign_id: uuid.UUID) -> BannerCampaign | None:
        return self._store.get(campaign_id)

    async def get_active(self, now: datetime) -> BannerCampaign | None:
        active = [c for c in self._store.values() if c.is_active_at(now)]
        return max(active, key=lambda c: (c.priority, c.starts_at), default=None)

    async def list_page(self, page: PageRequest) -> Page[BannerCampaign]:
        ordered = sorted(self._store.values(), key=lambda c: c.starts_at, reverse=True)
        return Page(
            items=tuple(ordered[page.offset : page.offset + page.limit]),
            total=len(ordered),
            limit=page.limit,
            offset=page.offset,
        )

    async def update(self, campaign: BannerCampaign) -> None:
        self._store[campaign.id] = campaign

    async def delete(self, campaign_id: uuid.UUID) -> bool:
        return self._store.pop(campaign_id, None) is not None


class FakeBannerUow:
    def __init__(self, store: dict[uuid.UUID, BannerCampaign]) -> None:
        self.banners = InMemoryBannerRepository(store)
        self.committed = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None: ...


class FakeMediaLookup:
    def __init__(self, known: dict[uuid.UUID, BannerImageDTO] | None = None) -> None:
        self.known = known or {}
        self.calls = 0

    async def get_images(self, ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, BannerImageDTO]:
        self.calls += 1
        return {i: self.known[i] for i in ids if i in self.known}


class FakeTagLookup:
    def __init__(self, slugs: set[str] | None = None) -> None:
        self.slugs = slugs or set()

    async def existing_slugs(self, slugs: Sequence[str]) -> set[str]:
        return {s for s in slugs if s in self.slugs}


class FakeAdminGuard:
    def __init__(self) -> None:
        self.tokens: list[str | None] = []

    def require_admin(self, token: str | None) -> None:
        self.tokens.append(token)
        if token != "good":
            from ups_kulka.shared.domain.errors import UnauthorizedError

            raise UnauthorizedError("no")
