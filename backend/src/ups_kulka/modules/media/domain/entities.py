import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from ups_kulka.modules.media.domain.errors import (
    ImageTooSmall,
    InvalidMediaFile,
    MediaFileTooLarge,
)

MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
MIN_IMAGE_DIMENSION_PX = 200
ALLOWED_MIME_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
STANDARD_WIDTHS = (320, 640, 960, 1280)


@dataclass(frozen=True, slots=True)
class MediaAsset:
    id: uuid.UUID
    original_filename: str
    mime_type: str
    file_size_bytes: int
    width: int
    height: int
    url_prefix: str
    blur_data_url: str
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        asset_id: uuid.UUID | None = None,
        original_filename: str,
        mime_type: str,
        file_size_bytes: int,
        width: int,
        height: int,
        blur_data_url: str,
    ) -> "MediaAsset":
        if file_size_bytes <= 0:
            raise InvalidMediaFile("Файл порожній")
        if file_size_bytes > MAX_FILE_SIZE_BYTES:
            raise MediaFileTooLarge
        clean_mime = mime_type.strip().lower()
        if clean_mime not in ALLOWED_MIME_TYPES:
            raise InvalidMediaFile
        if width < MIN_IMAGE_DIMENSION_PX or height < MIN_IMAGE_DIMENSION_PX:
            raise ImageTooSmall

        new_id = asset_id or uuid.uuid4()
        clean_name = (original_filename or "photo.jpg").strip()[:255] or "photo.jpg"
        return cls(
            id=new_id,
            original_filename=clean_name,
            mime_type=clean_mime,
            file_size_bytes=file_size_bytes,
            width=width,
            height=height,
            url_prefix=f"/media/{new_id}",
            blur_data_url=blur_data_url,
            created_at=datetime.now(UTC),
        )

    @property
    def variants(self) -> dict[str, str]:
        result = {f"{w}w": f"{self.url_prefix}/{w}w.webp" for w in STANDARD_WIDTHS}
        result["original"] = f"{self.url_prefix}/original.webp"
        return result
