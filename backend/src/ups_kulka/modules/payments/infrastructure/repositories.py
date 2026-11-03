from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ups_kulka.modules.payments.domain.entities import Payment, PaymentStatus
from ups_kulka.modules.payments.infrastructure.tables import PaymentRow
from ups_kulka.shared.domain.money import Money


def _to_domain(row: PaymentRow) -> Payment:
    return Payment(
        id=row.id,
        order_id=row.order_id,
        order_number=row.order_number,
        amount=Money(row.amount_kopecks),
        provider=row.provider,
        status=PaymentStatus(row.status),
        created_at=row.created_at,
        updated_at=row.updated_at,
        invoice_id=row.invoice_id,
        page_url=row.page_url,
    )


class SqlAlchemyPaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, payment: Payment) -> None:
        self._session.add(
            PaymentRow(
                id=payment.id,
                order_id=payment.order_id,
                order_number=payment.order_number,
                amount_kopecks=payment.amount.kopecks,
                provider=payment.provider,
                invoice_id=payment.invoice_id,
                page_url=payment.page_url,
                status=payment.status.value,
                created_at=payment.created_at,
                updated_at=payment.updated_at,
            )
        )
        await self._session.flush()

    async def get_by_invoice(self, invoice_id: str, *, for_update: bool = False) -> Payment | None:
        stmt = select(PaymentRow).where(PaymentRow.invoice_id == invoice_id)
        if for_update:
            stmt = stmt.with_for_update()
        row = await self._session.scalar(stmt)
        return _to_domain(row) if row is not None else None

    async def save(self, payment: Payment) -> None:
        await self._session.execute(
            update(PaymentRow)
            .where(PaymentRow.id == payment.id)
            .values(
                status=payment.status.value,
                updated_at=payment.updated_at,
                invoice_id=payment.invoice_id,
                page_url=payment.page_url,
            )
        )
