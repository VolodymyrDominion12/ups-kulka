from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker

from ups_kulka.modules.orders.application.use_cases.get_checkout_options import (
    GetCheckoutOptions,
)
from ups_kulka.modules.orders.application.use_cases.place_order import PlaceOrder
from ups_kulka.modules.orders.infrastructure.adapters import (
    CatalogProductCatalog,
    FacadePaymentStarter,
    NotificationsOrderNotifier,
)
from ups_kulka.modules.orders.infrastructure.uow import SqlAlchemyOrdersUnitOfWork


class OrdersContainer(containers.DeclarativeContainer):
    session_factory = providers.Dependency(instance_of=async_sessionmaker)
    # Public facades of other modules, provided by the root container. Typed as `object`:
    # a module container must not import other modules; the adapters below are typed exactly.
    catalog: providers.Dependency[object] = providers.Dependency()
    payments: providers.Dependency[object] = providers.Dependency()
    notifications: providers.Dependency[object] = providers.Dependency()

    uow = providers.Factory(SqlAlchemyOrdersUnitOfWork, session_factory=session_factory)
    product_catalog = providers.Factory(CatalogProductCatalog, catalog=catalog)
    payment_starter = providers.Factory(FacadePaymentStarter, payments=payments)
    notifier = providers.Factory(NotificationsOrderNotifier, notifications=notifications)

    place_order = providers.Factory(
        PlaceOrder,
        uow_factory=uow.provider,
        catalog=product_catalog,
        payments=payment_starter,
        notifier=notifier,
    )
    get_checkout_options = providers.Factory(GetCheckoutOptions, payments=payment_starter)
