from sqlalchemy.ext.asyncio import AsyncSession

from ups_kulka.modules.orders.infrastructure.repositories import SqlAlchemyOrderRepository
from ups_kulka.shared.infrastructure.db import SqlAlchemyUnitOfWork


class SqlAlchemyOrdersUnitOfWork(SqlAlchemyUnitOfWork):
    orders: SqlAlchemyOrderRepository

    def _init_repositories(self, session: AsyncSession) -> None:
        self.orders = SqlAlchemyOrderRepository(session)
