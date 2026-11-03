import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ups_kulka.modules.media.domain.entities import MediaAsset
from ups_kulka.modules.media.infrastructure.tables import MediaAssetRow
from ups_kulka.shared.application.pagination import Page, PageRequest


def media_to_domain(row: MediaAssetRow) -> MediaAsset:
    return MediaAsset(
        id=row.id,
        original_filename=row.original_filename,
        mime_type=row.mime_type,
        file_size_bytes=row.file_size_bytes,
        width=row.width,
        height=row.height,
        url_prefix=row.url_prefix,
        blur_data_url=row.blur_data_url,
        created_at=row.created_at,
    )


class SqlAlchemyMediaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, asset: MediaAsset) -> None:
        self._session.add(
            MediaAssetRow(
                id=asset.id,
                original_filename=asset.original_filename,
                mime_type=asset.mime_type,
                file_size_bytes=asset.file_size_bytes,
                width=asset.width,
                height=asset.height,
                url_prefix=asset.url_prefix,
                blur_data_url=asset.blur_data_url,
                created_at=asset.created_at,
            )
        )
        await self._session.flush()

    async def get_many(self, ids: Sequence[uuid.UUID]) -> list[MediaAsset]:
        if not ids:
            return []
        rows = await self._session.scalars(select(MediaAssetRow).where(MediaAssetRow.id.in_(ids)))
        return [media_to_domain(row) for row in rows]

    async def list_recent(self, page: PageRequest) -> Page[MediaAsset]:
        total = await self._session.scalar(select(func.count()).select_from(MediaAssetRow))
        rows = await self._session.scalars(
            select(MediaAssetRow)
            .order_by(MediaAssetRow.created_at.desc(), MediaAssetRow.id.desc())
            .limit(page.limit)
            .offset(page.offset)
        )
        return Page(
            items=tuple(media_to_domain(row) for row in rows),
            total=total or 0,
            limit=page.limit,
            offset=page.offset,
        )
