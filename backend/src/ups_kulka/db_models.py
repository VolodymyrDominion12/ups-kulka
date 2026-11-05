"""Imports every module's ORM tables so Alembic sees the full metadata.

Add a line here for each new module with tables.
"""

from ups_kulka.modules.banners.infrastructure import tables as banners_tables
from ups_kulka.modules.catalog.infrastructure import tables as catalog_tables
from ups_kulka.modules.media.infrastructure import tables as media_tables
from ups_kulka.modules.orders.infrastructure import tables as orders_tables
from ups_kulka.modules.payments.infrastructure import tables as payments_tables
from ups_kulka.shared.infrastructure.db import Base

metadata = Base.metadata

__all__ = [
    "banners_tables",
    "catalog_tables",
    "media_tables",
    "metadata",
    "orders_tables",
    "payments_tables",
]
