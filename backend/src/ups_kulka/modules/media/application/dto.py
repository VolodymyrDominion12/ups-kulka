import uuid
from dataclasses import dataclass
from datetime import datetime

from ups_kulka.modules.media.domain.entities import MediaAsset


@dataclass(frozen=True, slots=True)
class UploadMediaCommand:
    filename: str
    content_type: str
    content: bytes
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class ListMediaQuery:
    limit: int = 24
    offset: int = 0
    auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class ProcessedImage:
    mime_type: str
    width: int
    height: int
    blur_data_url: str
    files: dict[str, bytes]


@dataclass(frozen=True, slots=True)
class MediaAssetDTO:
    id: uuid.UUID
    original_filename: str
    mime_type: str
    file_size_bytes: int
    width: int
    height: int
    url_prefix: str
    blur_data_url: str
    variants: dict[str, str]
    created_at: datetime

    @classmethod
    def from_entity(cls, asset: MediaAsset) -> "MediaAssetDTO":
        return cls(
            id=asset.id,
            original_filename=asset.original_filename,
            mime_type=asset.mime_type,
            file_size_bytes=asset.file_size_bytes,
            width=asset.width,
            height=asset.height,
            url_prefix=asset.url_prefix,
            blur_data_url=asset.blur_data_url,
            variants=asset.variants,
            created_at=asset.created_at,
        )
