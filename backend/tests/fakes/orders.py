"""In-memory fakes of orders, payments and notifications ports (no DB, no network)."""

import uuid
from collections.abc import Mapping, Sequence
from datetime import date
from types import TracebackType
from typing import Self

from ups_kulka.modules.orders.application.dto import (
    CatalogProduct,
    CatalogProductAnalytics,
)
from ups_kulka.modules.orders.domain.entities import Order, OrderStatusEntry
from ups_kulka.modules.payments.application.dto import Invoice
from ups_kulka.modules.payments.domain.entities import Payment, PaymentStatus
from ups_kulka.shared.application.pagination import Page, PageRequest


class _FakeUoW:
    commits = 0

    def __call__(self) -> Self:
        return self

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        return None


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self.saved: list[Order] = []

    async def add(self, order: Order) -> int:
        self.saved.append(order)
        return 1000 + len(self.saved)

    async def get_by_number(self, number: int) -> Order | None:
        for o in self.saved:
            if o.number == number:
                return o
        return None

    async def save(self, order: Order, new_status_entry: OrderStatusEntry | None) -> None:
        for idx, existing in enumerate(self.saved):
            if existing.id == order.id:
                self.saved[idx] = order
                return

    async def list_for_admin(
        self,
        *,
        status: str | None,
        delivery_date: date | None,
        delivery_method: str | None,
        order_source: str | None,
        q: str | None,
        page: PageRequest,
    ) -> Page[Order]:
        items = list(self.saved)
        if status:
            items = [o for o in items if o.status.value == status]
        if delivery_date is not None:
            items = [o for o in items if o.delivery.date == delivery_date]
        if delivery_method:
            items = [o for o in items if o.delivery.method.value == delivery_method]
        if order_source:
            items = [o for o in items if o.marketing.order_source.value == order_source]
        if q and q.strip():
            needle = q.strip().lower()
            items = [
                o
                for o in items
                if needle in o.customer.name.lower()
                or needle in o.customer.phone.value.lower()
                or (o.number is not None and needle == str(o.number))
            ]
        items.sort(key=lambda o: (o.created_at, o.number or 0), reverse=True)
        return Page(
            items=tuple(items[page.offset : page.offset + page.limit]),
            total=len(items),
            limit=page.limit,
            offset=page.offset,
        )

    async def list_all_for_analytics(self) -> list[Order]:
        return list(self.saved)


class FakeOrdersUnitOfWork(_FakeUoW):
    def __init__(self) -> None:
        self.orders = InMemoryOrderRepository()


class FakeProductCatalog:
    def __init__(
        self,
        *products: CatalogProduct,
        analytics_products: list[CatalogProductAnalytics] | None = None,
    ) -> None:
        self.products = {p.id: p for p in products}
        self.analytics_products = analytics_products or []
        self.calls = 0

    async def products_for_order(
        self, ids: Sequence[uuid.UUID]
    ) -> Mapping[uuid.UUID, CatalogProduct]:
        self.calls += 1
        return {i: self.products[i] for i in ids if i in self.products}

    async def products_for_analytics(self) -> list[CatalogProductAnalytics]:
        return list(self.analytics_products)


class FakePaymentStarter:
    def __init__(self, *, enabled: bool = False, fail: bool = False) -> None:
        self._enabled = enabled
        self._fail = fail
        self.started: list[Order] = []

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    async def start(self, order: Order) -> str:
        if self._fail:
            raise RuntimeError("bank is down")
        self.started.append(order)
        return f"https://pay.example/{order.number}"


class RecordingOrderNotifier:
    def __init__(self, *, fail: bool = False) -> None:
        self._fail = fail
        self.sent: list[tuple[Order, str | None]] = []

    async def order_placed(self, order: Order, payment_url: str | None) -> None:
        if self._fail:
            raise RuntimeError("telegram is down")
        self.sent.append((order, payment_url))


class InMemoryPaymentRepository:
    def __init__(self) -> None:
        self.by_invoice: dict[str, Payment] = {}
        self.saves = 0

    async def add(self, payment: Payment) -> None:
        assert payment.invoice_id is not None
        self.by_invoice[payment.invoice_id] = payment

    async def get_by_invoice(self, invoice_id: str, *, for_update: bool = False) -> Payment | None:
        return self.by_invoice.get(invoice_id)

    async def save(self, payment: Payment) -> None:
        self.saves += 1


class FakePaymentsUnitOfWork(_FakeUoW):
    def __init__(self) -> None:
        self.payments = InMemoryPaymentRepository()


class FakePaymentGateway:
    provider = "fake"

    def __init__(self, status: PaymentStatus = PaymentStatus.PAID) -> None:
        self.status = status
        self.status_calls = 0

    async def create_invoice(self, payment: Payment, description: str) -> Invoice:
        return Invoice(invoice_id=f"inv-{payment.order_number}", page_url="https://pay.example/x")

    async def fetch_status(self, invoice_id: str) -> PaymentStatus:
        self.status_calls += 1
        return self.status


class RecordingPaymentNotifier:
    def __init__(self, *, fail: bool = False) -> None:
        self._fail = fail
        self.sent: list[int] = []

    async def payment_received(self, *, order_number: int, amount_kopecks: int) -> None:
        if self._fail:
            raise RuntimeError("telegram is down")
        self.sent.append(order_number)


class RecordingSender:
    def __init__(self) -> None:
        self.texts: list[str] = []

    async def send(self, text: str) -> None:
        self.texts.append(text)
