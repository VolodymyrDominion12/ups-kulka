"""Banners HTTP adapter (thin, see backend/AGENTS.md)."""

import uuid
from enum import Enum
from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, Query, Response, status

from ups_kulka.modules.banners.application.dto import (
    BannerIdCommand,
    ListBannerPresetsQuery,
    ListBannersQuery,
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
from ups_kulka.modules.banners.application.use_cases.get_active_banner import GetActiveBanner
from ups_kulka.modules.banners.application.use_cases.list_banner_presets import (
    ListBannerPresets,
)
from ups_kulka.modules.banners.presentation.schemas import (
    AdminBannerOut,
    AdminBannerPageOut,
    BannerCreateIn,
    BannerPresetOut,
    BannerUpdateIn,
    HomeBannerOut,
)
from ups_kulka.shared.application.pagination import DEFAULT_LIMIT, MAX_LIMIT
from ups_kulka.shared.presentation.errors import ErrorOut

router = APIRouter(prefix="/api/v1")

_ERRORS: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorOut},
    404: {"model": ErrorOut},
    422: {"model": ErrorOut},
}
_ADMIN = "/admin/banners"
_ADMIN_TAGS: list[str | Enum] = ["admin-banners"]

# No shared cache: the admin switches the hero manually, so it must change on the next request.
HOME_BANNER_CACHE = "no-store"


@router.get("/storefront/home-banner", tags=["storefront-banners"])
@inject
async def get_home_banner(
    response: Response,
    use_case: GetActiveBanner = Depends(Provide["banners.get_active_banner"]),
) -> HomeBannerOut:
    response.headers["Cache-Control"] = HOME_BANNER_CACHE
    return HomeBannerOut.from_dto(await use_case())


@router.get(_ADMIN, responses=_ERRORS, tags=_ADMIN_TAGS)
@inject
async def list_banners(
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    authorization: Annotated[str | None, Header()] = None,
    use_case: ListBanners = Depends(Provide["banners.list_banners"]),
) -> AdminBannerPageOut:
    query = ListBannersQuery(limit=limit, offset=offset, auth_token=authorization)
    return AdminBannerPageOut.from_page(await use_case(query))


@router.post(_ADMIN, status_code=status.HTTP_201_CREATED, responses=_ERRORS, tags=_ADMIN_TAGS)
@inject
async def create_banner(
    body: BannerCreateIn,
    authorization: Annotated[str | None, Header()] = None,
    use_case: CreateBanner = Depends(Provide["banners.create_banner"]),
) -> AdminBannerOut:
    return AdminBannerOut.from_dto(await use_case(body.to_command(authorization)))


@router.get(_ADMIN + "/presets", responses=_ERRORS, tags=_ADMIN_TAGS)
@inject
async def list_banner_presets(
    authorization: Annotated[str | None, Header()] = None,
    use_case: ListBannerPresets = Depends(Provide["banners.list_banner_presets"]),
) -> list[BannerPresetOut]:
    presets = await use_case(ListBannerPresetsQuery(auth_token=authorization))
    return [BannerPresetOut.from_dto(preset) for preset in presets]


@router.get(_ADMIN + "/{campaign_id}", responses=_ERRORS, tags=_ADMIN_TAGS)
@inject
async def get_banner(
    campaign_id: uuid.UUID,
    authorization: Annotated[str | None, Header()] = None,
    use_case: GetBanner = Depends(Provide["banners.get_banner"]),
) -> AdminBannerOut:
    return AdminBannerOut.from_dto(await use_case(BannerIdCommand(campaign_id, authorization)))


@router.patch(_ADMIN + "/{campaign_id}", responses=_ERRORS, tags=_ADMIN_TAGS)
@inject
async def update_banner(
    campaign_id: uuid.UUID,
    body: BannerUpdateIn,
    authorization: Annotated[str | None, Header()] = None,
    use_case: UpdateBanner = Depends(Provide["banners.update_banner"]),
) -> AdminBannerOut:
    return AdminBannerOut.from_dto(await use_case(body.to_command(campaign_id, authorization)))


@router.post(_ADMIN + "/{campaign_id}/publish", responses=_ERRORS, tags=_ADMIN_TAGS)
@inject
async def publish_banner(
    campaign_id: uuid.UUID,
    authorization: Annotated[str | None, Header()] = None,
    use_case: SetBannerPublished = Depends(Provide["banners.publish_banner"]),
) -> AdminBannerOut:
    return AdminBannerOut.from_dto(await use_case(BannerIdCommand(campaign_id, authorization)))


@router.post(_ADMIN + "/{campaign_id}/unpublish", responses=_ERRORS, tags=_ADMIN_TAGS)
@inject
async def unpublish_banner(
    campaign_id: uuid.UUID,
    authorization: Annotated[str | None, Header()] = None,
    use_case: SetBannerPublished = Depends(Provide["banners.unpublish_banner"]),
) -> AdminBannerOut:
    return AdminBannerOut.from_dto(await use_case(BannerIdCommand(campaign_id, authorization)))


@router.post(_ADMIN + "/{campaign_id}/activate", responses=_ERRORS, tags=_ADMIN_TAGS)
@inject
async def activate_banner(
    campaign_id: uuid.UUID,
    authorization: Annotated[str | None, Header()] = None,
    use_case: SetBannerPinned = Depends(Provide["banners.activate_banner"]),
) -> AdminBannerOut:
    """Show this campaign now, whatever its dates are."""
    return AdminBannerOut.from_dto(await use_case(BannerIdCommand(campaign_id, authorization)))


@router.post(_ADMIN + "/{campaign_id}/deactivate", responses=_ERRORS, tags=_ADMIN_TAGS)
@inject
async def deactivate_banner(
    campaign_id: uuid.UUID,
    authorization: Annotated[str | None, Header()] = None,
    use_case: SetBannerPinned = Depends(Provide["banners.deactivate_banner"]),
) -> AdminBannerOut:
    """Stop the manual override; the usual schedule applies again."""
    return AdminBannerOut.from_dto(await use_case(BannerIdCommand(campaign_id, authorization)))


@router.post(
    _ADMIN + "/{campaign_id}/duplicate",
    status_code=status.HTTP_201_CREATED,
    responses=_ERRORS,
    tags=_ADMIN_TAGS,
)
@inject
async def duplicate_banner(
    campaign_id: uuid.UUID,
    authorization: Annotated[str | None, Header()] = None,
    use_case: DuplicateBanner = Depends(Provide["banners.duplicate_banner"]),
) -> AdminBannerOut:
    return AdminBannerOut.from_dto(await use_case(BannerIdCommand(campaign_id, authorization)))


@router.delete(
    _ADMIN + "/{campaign_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=_ERRORS,
    tags=_ADMIN_TAGS,
)
@inject
async def delete_banner(
    campaign_id: uuid.UUID,
    authorization: Annotated[str | None, Header()] = None,
    use_case: DeleteBanner = Depends(Provide["banners.delete_banner"]),
) -> None:
    await use_case(BannerIdCommand(campaign_id, authorization))
