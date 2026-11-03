"""Composition root: the ONLY place that knows every layer and connects them."""

from dependency_injector import containers, providers

from ups_kulka.modules.catalog.container import CatalogContainer
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
