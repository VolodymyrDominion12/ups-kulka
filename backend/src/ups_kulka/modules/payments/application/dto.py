import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StartPaymentCommand:
    order_id: uuid.UUID
    order_number: int
    amount_kopecks: int
    description: str


@dataclass(frozen=True, slots=True)
class PaymentLinkDTO:
    payment_id: uuid.UUID
    page_url: str


@dataclass(frozen=True, slots=True)
class Invoice:
    invoice_id: str
    page_url: str
