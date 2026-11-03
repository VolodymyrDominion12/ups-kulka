import io
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from PIL import Image

from ups_kulka.modules.admin_auth.application.dto import LoginAdminCommand
from ups_kulka.modules.admin_auth.application.use_cases.login_admin import (
    LoginAdmin,
    VerifyAdminSession,
)
from ups_kulka.modules.admin_auth.domain.errors import (
    AdminSessionInvalid,
    InvalidAdminCredentials,
)
from ups_kulka.modules.admin_auth.infrastructure.tokens import HmacAdminTokenService
from ups_kulka.modules.media.application.dto import ListMediaQuery, UploadMediaCommand
from ups_kulka.modules.media.application.public import MediaFacade
from ups_kulka.modules.media.application.use_cases.list_media import ListMediaAssets
from ups_kulka.modules.media.application.use_cases.upload_media import UploadMedia
from ups_kulka.modules.media.domain.entities import MediaAsset
from ups_kulka.modules.media.domain.errors import (
    ImageTooSmall,
    InvalidMediaFile,
    MediaFileTooLarge,
)
from ups_kulka.modules.media.infrastructure.imaging import (
    LocalFileMediaStorage,
    PillowImageProcessor,
)
from ups_kulka.shared.application.pagination import Page, PageRequest


def _make_image_bytes(width: int = 800, height: int = 600, fmt: str = "JPEG") -> bytes:
    img = Image.new("RGB", (width, height), color=(230, 179, 179))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


class _FakeMediaRepo:
    def __init__(self) -> None:
        self.assets: list[MediaAsset] = []

    async def add(self, asset: MediaAsset) -> None:
        self.assets.append(asset)

    async def get_many(self, ids: list[uuid.UUID]) -> list[MediaAsset]:
        wanted = set(ids)
        return [a for a in self.assets if a.id in wanted]

    async def list_recent(self, page: PageRequest) -> Page[MediaAsset]:
        return Page(
            items=tuple(self.assets[page.offset : page.offset + page.limit]),
            total=len(self.assets),
            limit=page.limit,
            offset=page.offset,
        )


class _FakeMediaUoW:
    def __init__(self) -> None:
        self.media = _FakeMediaRepo()
        self.commits = 0

    def __call__(self) -> "_FakeMediaUoW":
        return self

    async def __aenter__(self) -> "_FakeMediaUoW":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        return None


async def test_admin_login_and_verify_token() -> None:
    now = datetime(2026, 11, 3, 12, 0, tzinfo=UTC)
    service = HmacAdminTokenService(
        admin_password="salon-secret",
        secret_key="test-hmac-key",
        now=lambda: now,
    )
    login = LoginAdmin(tokens=service)
    verify = VerifyAdminSession(tokens=service)

    session = await login(LoginAdminCommand(password="salon-secret"))
    assert session.role == "admin"
    assert session.token

    verified = await verify(f"Bearer {session.token}")
    assert verified.role == "admin"

    with pytest.raises(InvalidAdminCredentials):
        await login(LoginAdminCommand(password="wrong"))

    with pytest.raises(AdminSessionInvalid):
        await verify("Bearer tampered.token")

    with pytest.raises(AdminSessionInvalid):
        await verify(None)

    expired_service = HmacAdminTokenService(
        admin_password="salon-secret",
        secret_key="test-hmac-key",
        now=lambda: now + timedelta(days=31),
    )
    with pytest.raises(AdminSessionInvalid):
        expired_service.verify(session.token)


async def test_pillow_processor_and_upload_media(tmp_path: Path) -> None:
    uow = _FakeMediaUoW()
    processor = PillowImageProcessor()
    storage = LocalFileMediaStorage(str(tmp_path))
    upload = UploadMedia(uow_factory=uow, processor=processor, storage=storage)
    list_uc = ListMediaAssets(uow_factory=uow)
    facade = MediaFacade(uow_factory=uow)

    raw_jpeg = _make_image_bytes(width=1000, height=1000, fmt="JPEG")
    dto = await upload(
        UploadMediaCommand(
            filename="composition.jpg",
            content_type="image/jpeg",
            content=raw_jpeg,
        )
    )
    # 1000x1000 center-cropped to 4:5 becomes 800x1000
    assert dto.width == 800
    assert dto.height == 1000
    assert dto.blur_data_url.startswith("data:image/webp;base64,")
    assert "640w" in dto.variants
    assert (tmp_path / str(dto.id) / "640w.webp").is_file()

    page = await list_uc(ListMediaQuery(limit=10, offset=0))
    assert page.total == 1
    assert page.items[0].id == dto.id

    assets_map = await facade.get_assets([dto.id])
    assert dto.id in assets_map


async def test_upload_media_validation_errors(tmp_path: Path) -> None:
    uow = _FakeMediaUoW()
    processor = PillowImageProcessor()
    storage = LocalFileMediaStorage(str(tmp_path))
    upload = UploadMedia(uow_factory=uow, processor=processor, storage=storage)

    with pytest.raises(InvalidMediaFile):
        await upload(UploadMediaCommand(filename="a.jpg", content_type="image/jpeg", content=b""))

    with pytest.raises(InvalidMediaFile):
        await upload(
            UploadMediaCommand(filename="a.txt", content_type="text/plain", content=b"not-an-image")
        )

    small_img = _make_image_bytes(width=100, height=100)
    with pytest.raises(ImageTooSmall):
        await upload(
            UploadMediaCommand(filename="s.jpg", content_type="image/jpeg", content=small_img)
        )

    with pytest.raises(MediaFileTooLarge):
        MediaAsset.create(
            original_filename="huge.jpg",
            mime_type="image/jpeg",
            file_size_bytes=20 * 1024 * 1024,
            width=1000,
            height=1250,
            blur_data_url="data:image/webp;base64,AA",
        )
