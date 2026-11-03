from collections.abc import Callable
from typing import Protocol

from ups_kulka.modules.payments.application.dto import Invoice
from ups_kulka.modules.payments.domain.entities import Payment, PaymentStatus
from ups_kulka.shared.application.uow import UnitOfWork


class PaymentGateway(Protocol):
    """An acquiring provider. monobank first; LiqPay/WayForPay implement the same port."""

    provider: str

    async def create_invoice(self, payment: Payment, description: str) -> Invoice: ...

    async def fetch_status(self, invoice_id: str) -> PaymentStatus:
        """Authoritative status asked from the provider with our own credentials."""
        ...


class PaymentRepository(Protocol):
    async def add(self, payment: Payment) -> None: ...

    async def get_by_invoice(self, invoice_id: str, *, for_update: bool = False) -> Payment | None:
        """``for_update`` locks the row so parallel webhooks are applied one by one."""
        ...

    async def save(self, payment: Payment) -> None: ...


class PaymentNotifier(Protocol):
    async def payment_received(self, *, order_number: int, amount_kopecks: int) -> None: ...


class PaymentsUnitOfWork(UnitOfWork, Protocol):
    payments: PaymentRepository


type PaymentsUnitOfWorkFactory = Callable[[], PaymentsUnitOfWork]
