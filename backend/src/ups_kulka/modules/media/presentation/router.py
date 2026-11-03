"""Media HTTP adapter (thin, see backend/AGENTS.md)."""

from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Header, Query, UploadFile, status

from ups_kulka.modules.media.application.dto import ListMediaQuery, UploadMediaCommand
from ups_kulka.modules.media.application.use_cases.list_media import ListMediaAssets
from ups_kulka.modules.media.application.use_cases.upload_media import UploadMedia
from ups_kulka.modules.media.presentation.schemas import MediaAssetOut, MediaAssetPageOut
from ups_kulka.shared.application.pagination import DEFAULT_LIMIT, MAX_LIMIT
from ups_kulka.shared.presentation.errors import ErrorOut

router = APIRouter(prefix="/api/v1/admin/media", tags=["admin-media"])

_ERRORS: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorOut},
    422: {"model": ErrorOut},
}


@router.post("", status_code=status.HTTP_201_CREATED, responses=_ERRORS)
@inject
async def upload_media(
    file: Annotated[UploadFile, File(...)],
    authorization: Annotated[str | None, Header()] = None,
    use_case: UploadMedia = Depends(Provide["media.upload_media"]),
) -> MediaAssetOut:
    cmd = UploadMediaCommand(
        filename=file.filename or "photo.jpg",
        content_type=file.content_type or "image/jpeg",
        content=file.file.read(),
        auth_token=authorization,
    )
    return MediaAssetOut.from_dto(await use_case(cmd))


@router.get("", responses=_ERRORS)
@inject
async def list_media(
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    authorization: Annotated[str | None, Header()] = None,
    use_case: ListMediaAssets = Depends(Provide["media.list_media"]),
) -> MediaAssetPageOut:
    query = ListMediaQuery(limit=limit, offset=offset, auth_token=authorization)
    return MediaAssetPageOut.from_page(await use_case(query))
