from sqlalchemy.ext.asyncio import AsyncSession

from ups_kulka.modules.payments.infrastructure.repositories import SqlAlchemyPaymentRepository
from ups_kulka.shared.infrastructure.db import SqlAlchemyUnitOfWork


class SqlAlchemyPaymentsUnitOfWork(SqlAlchemyUnitOfWork):
    payments: SqlAlchemyPaymentRepository

    def _init_repositories(self, session: AsyncSession) -> None:
        self.payments = SqlAlchemyPaymentRepository(session)
