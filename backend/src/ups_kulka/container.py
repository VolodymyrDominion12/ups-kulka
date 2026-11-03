"""Composition root: the ONLY place that knows every layer and connects them."""

from dependency_injector import containers, providers

from ups_kulka.modules.catalog.container import CatalogContainer
from ups_kulka.modules.notifications.container import NotificationsContainer
from ups_kulka.modules.orders.container import OrdersContainer
from ups_kulka.modules.payments.container import PaymentsContainer
from ups_kulka.settings import Settings
from ups_kulka.shared.infrastructure.db import create_engine, create_session_factory


class Container(containers.DeclarativeContainer):
    settings = providers.Singleton(Settings)

    engine = providers.Singleton(
        create_engine,
        database_url=settings.provided.database_url,
        echo=settings.provided.sql_echo,
    )
    session_factory = providers.Singleton(create_session_factory, engine=engine)

    # One sub-container per module; add new modules here.
    catalog = providers.Container(CatalogContainer, session_factory=session_factory)
    notifications = providers.Container(
        NotificationsContainer,
        telegram_bot_token=settings.provided.telegram_bot_token,
        telegram_chat_id=settings.provided.telegram_chat_id,
    )
    payments = providers.Container(
        PaymentsContainer,
        session_factory=session_factory,
        monobank_token=settings.provided.monobank_token,
        public_base_url=settings.provided.public_base_url,
        notifications=notifications.facade,
    )
    # Modules talk to each other only through public facades, connected here.
    orders = providers.Container(
        OrdersContainer,
        session_factory=session_factory,
        catalog=catalog.facade,
        payments=payments.facade,
        notifications=notifications.facade,
    )
