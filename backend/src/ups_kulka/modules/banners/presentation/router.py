"""Banners HTTP adapter (thin, see backend/AGENTS.md)."""

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response

from ups_kulka.modules.banners.application.use_cases.get_active_banner import GetActiveBanner
from ups_kulka.modules.banners.presentation.schemas import HomeBannerOut

router = APIRouter(prefix="/api/v1/storefront", tags=["storefront-banners"])

# Short shared cache: a campaign switch shows up within a minute without a deploy.
HOME_BANNER_CACHE = "public, s-maxage=60, stale-while-revalidate=120"


@router.get("/home-banner")
@inject
async def get_home_banner(
    response: Response,
    use_case: GetActiveBanner = Depends(Provide["banners.get_active_banner"]),
) -> HomeBannerOut:
    response.headers["Cache-Control"] = HOME_BANNER_CACHE
    return HomeBannerOut.from_dto(await use_case())
