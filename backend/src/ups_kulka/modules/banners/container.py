from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker

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
from ups_kulka.modules.banners.infrastructure.adapters import (
    BannerAdminAuthAdapter,
    CatalogTagAdapter,
    MediaBannerAdapter,
)
from ups_kulka.modules.banners.infrastructure.uow import SqlAlchemyBannerUnitOfWork


class BannersContainer(containers.DeclarativeContainer):
    session_factory = providers.Dependency(instance_of=async_sessionmaker)
    media: providers.Dependency[object] = providers.Dependency()
    catalog: providers.Dependency[object] = providers.Dependency()
    admin_auth: providers.Dependency[object] = providers.Dependency()

    uow = providers.Factory(SqlAlchemyBannerUnitOfWork, session_factory=session_factory)
    media_lookup = providers.Factory(MediaBannerAdapter, media=media)

    get_active_banner = providers.Factory(
        GetActiveBanner,
        uow_factory=uow.provider,
        media=media_lookup,
    )
    tag_lookup = providers.Factory(CatalogTagAdapter, catalog=catalog)
    auth_adapter = providers.Factory(BannerAdminAuthAdapter, auth=admin_auth)

    list_banners = providers.Factory(
        ListBanners, uow_factory=uow.provider, media=media_lookup, auth=auth_adapter
    )
    get_banner = providers.Factory(
        GetBanner, uow_factory=uow.provider, media=media_lookup, auth=auth_adapter
    )
    create_banner = providers.Factory(
        CreateBanner,
        uow_factory=uow.provider,
        media=media_lookup,
        tags=tag_lookup,
        auth=auth_adapter,
    )
    update_banner = providers.Factory(
        UpdateBanner,
        uow_factory=uow.provider,
        media=media_lookup,
        tags=tag_lookup,
        auth=auth_adapter,
    )
    publish_banner = providers.Factory(
        SetBannerPublished,
        uow_factory=uow.provider,
        media=media_lookup,
        published=True,
        auth=auth_adapter,
    )
    unpublish_banner = providers.Factory(
        SetBannerPublished,
        uow_factory=uow.provider,
        media=media_lookup,
        published=False,
        auth=auth_adapter,
    )
    activate_banner = providers.Factory(
        SetBannerPinned,
        uow_factory=uow.provider,
        media=media_lookup,
        pinned=True,
        auth=auth_adapter,
    )
    deactivate_banner = providers.Factory(
        SetBannerPinned,
        uow_factory=uow.provider,
        media=media_lookup,
        pinned=False,
        auth=auth_adapter,
    )
    list_banner_presets = providers.Factory(ListBannerPresets, auth=auth_adapter)
    duplicate_banner = providers.Factory(
        DuplicateBanner, uow_factory=uow.provider, media=media_lookup, auth=auth_adapter
    )
    delete_banner = providers.Factory(
        DeleteBanner, uow_factory=uow.provider, media=media_lookup, auth=auth_adapter
    )
