"""Imports every module's ORM tables so Alembic sees the full metadata.

Add a line here for each new module with tables.
"""

from ups_kulka.modules.catalog.infrastructure import tables as catalog_tables
from ups_kulka.shared.infrastructure.db import Base

metadata = Base.metadata

__all__ = ["catalog_tables", "metadata"]
