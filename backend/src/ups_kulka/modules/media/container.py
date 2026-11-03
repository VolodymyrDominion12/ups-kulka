from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker

from ups_kulka.modules.media.application.public import MediaFacade
from ups_kulka.modules.media.application.use_cases.list_media import ListMediaAssets
from ups_kulka.modules.media.application.use_cases.upload_media import UploadMedia
from ups_kulka.modules.media.infrastructure.adapters import AdminAuthAdapter
from ups_kulka.modules.media.infrastructure.imaging import (
    LocalFileMediaStorage,
    PillowImageProcessor,
)
from ups_kulka.modules.media.infrastructure.uow import SqlAlchemyMediaUnitOfWork


class MediaContainer(containers.DeclarativeContainer):
    session_factory = providers.Dependency(instance_of=async_sessionmaker)
    media_root = providers.Dependency(instance_of=str)
    admin_auth: providers.Dependency[object] = providers.Dependency()

    uow = providers.Factory(
        SqlAlchemyMediaUnitOfWork,
        session_factory=session_factory,
    )
    auth_adapter = providers.Factory(AdminAuthAdapter, auth=admin_auth)
    processor = providers.Singleton(PillowImageProcessor)
    storage = providers.Singleton(LocalFileMediaStorage, media_root=media_root)

    upload_media = providers.Factory(
        UploadMedia,
        uow_factory=uow.provider,
        processor=processor,
        storage=storage,
        auth=auth_adapter,
    )
    list_media = providers.Factory(
        ListMediaAssets,
        uow_factory=uow.provider,
        auth=auth_adapter,
    )
    facade = providers.Factory(MediaFacade, uow_factory=uow.provider)
