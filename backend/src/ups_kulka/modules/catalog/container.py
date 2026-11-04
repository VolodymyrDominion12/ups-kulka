from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker

from ups_kulka.modules.catalog.application.public import CatalogFacade
from ups_kulka.modules.catalog.application.use_cases.admin_products import (
    ListAdminProducts,
    QuickCreateProduct,
    UpdateProduct,
)
from ups_kulka.modules.catalog.application.use_cases.create_product import CreateProduct
from ups_kulka.modules.catalog.application.use_cases.create_tag import CreateTag
from ups_kulka.modules.catalog.application.use_cases.get_product import GetProduct
from ups_kulka.modules.catalog.application.use_cases.get_tag_detail import GetTagDetail
from ups_kulka.modules.catalog.application.use_cases.import_legacy_photos import (
    ImportLegacyPhotos,
)
from ups_kulka.modules.catalog.application.use_cases.list_products import ListProducts
from ups_kulka.modules.catalog.application.use_cases.list_tags import ListTags
from ups_kulka.modules.catalog.application.use_cases.update_tag_seo import UpdateTagSeo
from ups_kulka.modules.catalog.infrastructure.adapters import (
    CatalogAdminAuthAdapter,
    HttpPhotoDownloader,
    MediaCatalogAdapter,
    MediaPhotoUploader,
)
from ups_kulka.modules.catalog.infrastructure.uow import SqlAlchemyCatalogUnitOfWork


class CatalogContainer(containers.DeclarativeContainer):
    """Wires catalog ports to implementations. Shared resources come from the root."""

    session_factory = providers.Dependency(instance_of=async_sessionmaker)
    media: providers.Dependency[object] = providers.Dependency()
    admin_auth: providers.Dependency[object] = providers.Dependency()

    uow = providers.Factory(SqlAlchemyCatalogUnitOfWork, session_factory=session_factory)
    media_lookup = providers.Factory(MediaCatalogAdapter, media=media)
    auth_adapter = providers.Factory(CatalogAdminAuthAdapter, auth=admin_auth)

    # `.provider` injects the factory itself: each call opens a NEW unit of work.
    create_tag = providers.Factory(CreateTag, uow_factory=uow.provider)
    list_tags = providers.Factory(ListTags, uow_factory=uow.provider)
    get_tag_detail = providers.Factory(GetTagDetail, uow_factory=uow.provider)
    update_tag_seo = providers.Factory(UpdateTagSeo, uow_factory=uow.provider, auth=auth_adapter)
    create_product = providers.Factory(
        CreateProduct,
        uow_factory=uow.provider,
        media_lookup=media_lookup,
    )
    get_product = providers.Factory(GetProduct, uow_factory=uow.provider)
    list_products = providers.Factory(ListProducts, uow_factory=uow.provider)

    quick_create_product = providers.Factory(
        QuickCreateProduct,
        uow_factory=uow.provider,
        media_lookup=media_lookup,
        auth=auth_adapter,
    )
    update_product = providers.Factory(
        UpdateProduct,
        uow_factory=uow.provider,
        media_lookup=media_lookup,
        auth=auth_adapter,
    )
    list_admin_products = providers.Factory(
        ListAdminProducts,
        uow_factory=uow.provider,
        auth=auth_adapter,
    )

    # Public facade for other modules (orders reads prices through it).
    facade = providers.Factory(CatalogFacade, uow_factory=uow.provider)

    # One-off migration of the old site's photos (scripts/import_old_site.py, specs/010).
    photo_downloader = providers.Factory(HttpPhotoDownloader)
    photo_uploader = providers.Factory(MediaPhotoUploader, media=media)
    import_legacy_photos = providers.Factory(
        ImportLegacyPhotos,
        uow_factory=uow.provider,
        media_lookup=media_lookup,
        downloader=photo_downloader,
        uploader=photo_uploader,
    )
