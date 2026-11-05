from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker

from ups_kulka.modules.banners.application.use_cases.get_active_banner import GetActiveBanner
from ups_kulka.modules.banners.infrastructure.adapters import MediaBannerAdapter
from ups_kulka.modules.banners.infrastructure.uow import SqlAlchemyBannerUnitOfWork


class BannersContainer(containers.DeclarativeContainer):
    session_factory = providers.Dependency(instance_of=async_sessionmaker)
    media: providers.Dependency[object] = providers.Dependency()

    uow = providers.Factory(SqlAlchemyBannerUnitOfWork, session_factory=session_factory)
    media_lookup = providers.Factory(MediaBannerAdapter, media=media)

    get_active_banner = providers.Factory(
        GetActiveBanner,
        uow_factory=uow.provider,
        media=media_lookup,
    )
