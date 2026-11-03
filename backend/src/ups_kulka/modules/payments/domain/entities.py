import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from ups_kulka.modules.payments.domain.errors import InvalidPayment
from ups_kulka.shared.domain.money import Money


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


# Allowed transitions. Anything else (e.g. paid -> pending from a late webhook) is ignored.
_TRANSITIONS: dict[PaymentStatus, frozenset[PaymentStatus]] = {
    PaymentStatus.PENDING: frozenset({PaymentStatus.PAID, PaymentStatus.FAILED}),
    PaymentStatus.FAILED: frozenset({PaymentStatus.PAID}),
    PaymentStatus.PAID: frozenset({PaymentStatus.REFUNDED}),
    PaymentStatus.REFUNDED: frozenset(),
}


@dataclass(slots=True)
class Payment:
    id: uuid.UUID
    order_id: uuid.UUID
    order_number: int
    amount: Money
    provider: str
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    invoice_id: str | None = None
    page_url: str | None = None

    @classmethod
    def create(
        cls, *, order_id: uuid.UUID, order_number: int, amount: Money, provider: str
    ) -> "Payment":
        if amount.is_zero:
            raise InvalidPayment("Payment amount must be greater than zero")
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            order_id=order_id,
            order_number=order_number,
            amount=amount,
            provider=provider,
            status=PaymentStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

    def attach_invoice(self, invoice_id: str, page_url: str) -> None:
        if not invoice_id or not page_url:
            raise InvalidPayment("Invoice id and payment page URL are required")
        self.invoice_id = invoice_id
        self.page_url = page_url

    def apply(self, status: PaymentStatus) -> bool:
        """Apply a status reported by the provider. Returns True if anything changed.

        Idempotent: a repeated or out-of-order webhook does not change a final state.
        """
        if status not in _TRANSITIONS[self.status]:
            return False
        self.status = status
        self.updated_at = datetime.now(UTC)
        return True

    @property
    def is_paid(self) -> bool:
        return self.status is PaymentStatus.PAID
