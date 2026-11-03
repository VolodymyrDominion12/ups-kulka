from sqlalchemy.ext.asyncio import AsyncSession

from ups_kulka.modules.catalog.infrastructure.repositories import (
    SqlAlchemyProductRepository,
    SqlAlchemyTagRepository,
)
from ups_kulka.shared.infrastructure.db import SqlAlchemyUnitOfWork


class SqlAlchemyCatalogUnitOfWork(SqlAlchemyUnitOfWork):
    products: SqlAlchemyProductRepository
    tags: SqlAlchemyTagRepository

    def _init_repositories(self, session: AsyncSession) -> None:
        self.products = SqlAlchemyProductRepository(session)
        self.tags = SqlAlchemyTagRepository(session)
