import uuid
from datetime import datetime

from pydantic import BaseModel

from ups_kulka.modules.media.application.dto import MediaAssetDTO
from ups_kulka.shared.application.pagination import Page


class MediaAssetOut(BaseModel):
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
    def from_dto(cls, dto: MediaAssetDTO) -> "MediaAssetOut":
        return cls(
            id=dto.id,
            original_filename=dto.original_filename,
            mime_type=dto.mime_type,
            file_size_bytes=dto.file_size_bytes,
            width=dto.width,
            height=dto.height,
            url_prefix=dto.url_prefix,
            blur_data_url=dto.blur_data_url,
            variants=dto.variants,
            created_at=dto.created_at,
        )


class MediaAssetPageOut(BaseModel):
    items: list[MediaAssetOut]
    total: int
    limit: int
    offset: int

    @classmethod
    def from_page(cls, page: Page[MediaAssetDTO]) -> "MediaAssetPageOut":
        return cls(
            items=[MediaAssetOut.from_dto(item) for item in page.items],
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )
