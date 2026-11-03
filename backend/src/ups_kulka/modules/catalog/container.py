from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker

from ups_kulka.modules.catalog.application.use_cases.create_product import CreateProduct
from ups_kulka.modules.catalog.application.use_cases.create_tag import CreateTag
from ups_kulka.modules.catalog.application.use_cases.get_product import GetProduct
from ups_kulka.modules.catalog.application.use_cases.list_products import ListProducts
from ups_kulka.modules.catalog.infrastructure.uow import SqlAlchemyCatalogUnitOfWork


class CatalogContainer(containers.DeclarativeContainer):
    """Wires catalog ports to implementations. Shared resources come from the root."""

    session_factory = providers.Dependency(instance_of=async_sessionmaker)

    uow = providers.Factory(SqlAlchemyCatalogUnitOfWork, session_factory=session_factory)

    # `.provider` injects the factory itself: each call opens a NEW unit of work.
    create_tag = providers.Factory(CreateTag, uow_factory=uow.provider)
    create_product = providers.Factory(CreateProduct, uow_factory=uow.provider)
    get_product = providers.Factory(GetProduct, uow_factory=uow.provider)
    list_products = providers.Factory(ListProducts, uow_factory=uow.provider)
