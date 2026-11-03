from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker

from ups_kulka.modules.payments.application.public import PaymentsFacade
from ups_kulka.modules.payments.application.use_cases.confirm_payment import ConfirmPayment
from ups_kulka.modules.payments.application.use_cases.start_payment import StartPayment
from ups_kulka.modules.payments.infrastructure.adapters import NotificationsPaymentNotifier
from ups_kulka.modules.payments.infrastructure.monobank import make_gateway
from ups_kulka.modules.payments.infrastructure.uow import SqlAlchemyPaymentsUnitOfWork


class PaymentsContainer(containers.DeclarativeContainer):
    session_factory = providers.Dependency(instance_of=async_sessionmaker)
    monobank_token = providers.Dependency(instance_of=str, default="")
    public_base_url = providers.Dependency(instance_of=str, default="")
    # NotificationsFacade from the root container. Typed as `object`: a module container
    # must not import other modules; NotificationsPaymentNotifier is typed exactly.
    notifications: providers.Dependency[object] = providers.Dependency()

    uow = providers.Factory(SqlAlchemyPaymentsUnitOfWork, session_factory=session_factory)
    # None when no token: online payment is off. Tests override it with a fake gateway.
    gateway = providers.Singleton(
        make_gateway, monobank_token=monobank_token, public_base_url=public_base_url
    )
    notifier = providers.Factory(NotificationsPaymentNotifier, notifications=notifications)

    start_payment = providers.Factory(StartPayment, uow_factory=uow.provider, gateway=gateway)
    confirm_payment = providers.Factory(
        ConfirmPayment, uow_factory=uow.provider, gateway=gateway, notifier=notifier
    )

    facade = providers.Factory(PaymentsFacade, start_payment=start_payment)
