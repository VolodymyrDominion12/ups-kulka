import uuid
from datetime import UTC, datetime

import pytest

from tests.fakes.banners import (
    IMAGE,
    FakeAdminGuard,
    FakeBannerUow,
    FakeMediaLookup,
    FakeTagLookup,
)
from ups_kulka.modules.banners.application.dto import (
    BannerIdCommand,
    CreateBannerCommand,
    ListBannersQuery,
    UpdateBannerCommand,
)
from ups_kulka.modules.banners.application.use_cases.admin_banners import (
    CreateBanner,
    DeleteBanner,
    DuplicateBanner,
    GetBanner,
    ListBanners,
    SetBannerPinned,
    SetBannerPublished,
    UpdateBanner,
)
from ups_kulka.modules.banners.domain.entities import BannerCampaign, BannerState
from ups_kulka.modules.banners.domain.errors import (
    BannerImageNotFound,
    BannerNotFound,
    BannerTagNotFound,
    InvalidBannerPeriod,
)
from ups_kulka.shared.domain.errors import UnauthorizedError

NOW = datetime(2027, 3, 5, tzinfo=UTC)
START = datetime(2027, 3, 1, tzinfo=UTC)
END = datetime(2027, 3, 9, tzinfo=UTC)
TOKEN = "good"


class Env:
    def __init__(self) -> None:
        self.store: dict[uuid.UUID, BannerCampaign] = {}
        self.media_id = uuid.uuid4()
        self.media = FakeMediaLookup({self.media_id: IMAGE})
        self.tags = FakeTagLookup({"8-bereznia"})
        self.guard = FakeAdminGuard()

    def uow(self) -> FakeBannerUow:
        return FakeBannerUow(self.store)

    def _kw(self) -> dict[str, object]:
        return {
            "uow_factory": self.uow,
            "media": self.media,
            "auth": self.guard,
            "clock": lambda: NOW,
        }

    def create(self) -> CreateBanner:
        return CreateBanner(tags=self.tags, **self._kw())  # type: ignore[arg-type]

    def update(self) -> UpdateBanner:
        return UpdateBanner(tags=self.tags, **self._kw())  # type: ignore[arg-type]

    def list(self) -> ListBanners:
        return ListBanners(**self._kw())  # type: ignore[arg-type]

    def get(self) -> GetBanner:
        return GetBanner(**self._kw())  # type: ignore[arg-type]

    def publish(self, published: bool = True) -> SetBannerPublished:
        return SetBannerPublished(published=published, **self._kw())  # type: ignore[arg-type]

    def pin(self, pinned: bool = True) -> SetBannerPinned:
        return SetBannerPinned(pinned=pinned, **self._kw())  # type: ignore[arg-type]

    def duplicate(self) -> DuplicateBanner:
        return DuplicateBanner(**self._kw())  # type: ignore[arg-type]

    def delete(self) -> DeleteBanner:
        return DeleteBanner(**self._kw())  # type: ignore[arg-type]


def command(**overrides: object) -> CreateBannerCommand:
    params: dict[str, object] = {
        "name": "8 Березня 2027",
        "layout": "balloons",
        "starts_at": START,
        "ends_at": END,
        "headline": "З 8 Березня!",
        "auth_token": TOKEN,
    }
    params.update(overrides)
    return CreateBannerCommand(**params)  # type: ignore[arg-type]


@pytest.fixture
def env() -> Env:
    return Env()


async def test_admin_token_is_required(env: Env) -> None:
    with pytest.raises(UnauthorizedError):
        await env.create()(command(auth_token="bad"))
    with pytest.raises(UnauthorizedError):
        await env.list()(ListBannersQuery(auth_token=None))
    assert env.store == {}


async def test_create_returns_draft_and_persists(env: Env) -> None:
    dto = await env.create()(command())
    assert dto.state is BannerState.DRAFT
    assert dto.id in env.store


async def test_create_with_image_resolves_it(env: Env) -> None:
    dto = await env.create()(command(layout="image", media_id=env.media_id))
    assert dto.image == IMAGE


async def test_create_rejects_unknown_photo(env: Env) -> None:
    with pytest.raises(BannerImageNotFound):
        await env.create()(command(layout="image", media_id=uuid.uuid4()))
    assert env.store == {}


async def test_collection_requires_existing_tag(env: Env) -> None:
    with pytest.raises(BannerTagNotFound):
        await env.create()(command(layout="collection", tag_slug="nope"))
    dto = await env.create()(command(layout="collection", tag_slug="8-bereznia"))
    assert dto.tag_slug == "8-bereznia"


async def test_update_changes_only_sent_fields(env: Env) -> None:
    created = await env.create()(command(priority=1))
    updated = await env.update()(
        UpdateBannerCommand(created.id, {"headline": "Нове", "theme": "red"}, TOKEN)
    )
    assert updated.headline == "Нове"
    assert updated.theme.value == "red"
    assert updated.priority == 1
    assert updated.name == created.name


async def test_update_validates_and_does_not_save_invalid(env: Env) -> None:
    created = await env.create()(command())
    with pytest.raises(InvalidBannerPeriod):
        await env.update()(UpdateBannerCommand(created.id, {"ends_at": START}, TOKEN))
    assert env.store[created.id].ends_at == END


async def test_update_unknown_banner(env: Env) -> None:
    with pytest.raises(BannerNotFound):
        await env.update()(UpdateBannerCommand(uuid.uuid4(), {"headline": "x"}, TOKEN))


async def test_publish_and_unpublish_change_state(env: Env) -> None:
    created = await env.create()(command())
    cmd = BannerIdCommand(created.id, TOKEN)
    published = await env.publish(True)(cmd)
    assert published.state is BannerState.ACTIVE
    assert (await env.publish(False)(cmd)).state is BannerState.DRAFT


async def test_activate_publishes_and_pins_a_draft(env: Env) -> None:
    future = command(
        starts_at=datetime(2027, 5, 1, tzinfo=UTC),
        ends_at=datetime(2027, 5, 10, tzinfo=UTC),
    )
    created = await env.create()(future)

    activated = await env.pin(True)(BannerIdCommand(created.id, TOKEN))

    assert activated.pinned is True
    assert activated.status == "published"
    assert activated.state is BannerState.ACTIVE  # pinned, even though the dates are ahead
    assert env.store[created.id].pinned is True


async def test_activate_unpins_the_previous_campaign(env: Env) -> None:
    first = await env.create()(command(name="first"))
    second = await env.create()(command(name="second"))
    await env.pin(True)(BannerIdCommand(first.id, TOKEN))
    await env.pin(True)(BannerIdCommand(second.id, TOKEN))

    pinned = [c for c in env.store.values() if c.pinned]
    assert [c.id for c in pinned] == [second.id]


async def test_deactivate_returns_to_the_schedule(env: Env) -> None:
    future = command(
        starts_at=datetime(2027, 5, 1, tzinfo=UTC),
        ends_at=datetime(2027, 5, 10, tzinfo=UTC),
    )
    created = await env.create()(future)
    cmd = BannerIdCommand(created.id, TOKEN)
    await env.pin(True)(cmd)

    restored = await env.pin(False)(cmd)

    assert restored.pinned is False
    assert restored.state is BannerState.SCHEDULED
    assert env.store[created.id].pinned is False


async def test_unpublish_clears_the_manual_override(env: Env) -> None:
    created = await env.create()(command())
    cmd = BannerIdCommand(created.id, TOKEN)
    await env.pin(True)(cmd)

    unpublished = await env.publish(False)(cmd)

    assert unpublished.pinned is False
    assert unpublished.state is BannerState.DRAFT


async def test_pin_requires_admin_and_an_existing_campaign(env: Env) -> None:
    created = await env.create()(command())
    with pytest.raises(UnauthorizedError):
        await env.pin(True)(BannerIdCommand(created.id, "bad"))
    with pytest.raises(BannerNotFound):
        await env.pin(True)(BannerIdCommand(uuid.uuid4(), TOKEN))


async def test_duplicate_makes_next_year_draft(env: Env) -> None:
    created = await env.create()(command())
    await env.publish(True)(BannerIdCommand(created.id, TOKEN))
    copy = await env.duplicate()(BannerIdCommand(created.id, TOKEN))
    assert copy.id != created.id
    assert copy.state is BannerState.DRAFT
    assert copy.name.endswith("(копія)")
    assert copy.starts_at.year == 2028
    assert len(env.store) == 2


async def test_delete_and_missing(env: Env) -> None:
    created = await env.create()(command())
    await env.delete()(BannerIdCommand(created.id, TOKEN))
    assert env.store == {}
    with pytest.raises(BannerNotFound):
        await env.delete()(BannerIdCommand(created.id, TOKEN))
    with pytest.raises(BannerNotFound):
        await env.get()(BannerIdCommand(created.id, TOKEN))


async def test_list_uses_one_media_lookup_for_all_items(env: Env) -> None:
    for i in range(5):
        await env.create()(command(layout="image", media_id=env.media_id, name=f"c{i}"))
    env.media.calls = 0
    page = await env.list()(ListBannersQuery(auth_token=TOKEN))
    assert page.total == 5
    assert all(item.image == IMAGE for item in page.items)
    assert env.media.calls == 1
