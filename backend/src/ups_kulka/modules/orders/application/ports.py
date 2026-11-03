import uuid
from collections.abc import Callable, Mapping, Sequence
from datetime import date
from typing import Protocol

from ups_kulka.modules.orders.application.dto import (
    CatalogProduct,
    CatalogProductAnalytics,
    CustomerCrmDTO,
    OrderAnniversaryDTO,
)
from ups_kulka.modules.orders.domain.entities import Order, OrderStatusEntry
from ups_kulka.shared.application.pagination import Page, PageRequest
from ups_kulka.shared.application.uow import UnitOfWork


class OrdersAdminGuard(Protocol):
    def require_admin(self, token: str | None) -> None: ...


class OrderRepository(Protocol):
    async def add(self, order: Order) -> int:
        """Saves the order with its items (constant number of queries); returns its number."""
        ...

    async def get_by_number(self, number: int) -> Order | None: ...

    async def save(self, order: Order, new_status_entry: OrderStatusEntry | None) -> None: ...

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
        """Must run a constant number of queries regardless of page size (no N+1)."""
        ...

    async def list_all_for_analytics(self) -> list[Order]:
        """Loads orders with items in 2 constant queries for analytics/CRM calculations."""
        ...


class OrdersUnitOfWork(UnitOfWork, Protocol):
    orders: OrderRepository


type OrdersUnitOfWorkFactory = Callable[[], OrdersUnitOfWork]


class ProductCatalog(Protocol):
    async def products_for_order(
        self, ids: Sequence[uuid.UUID]
    ) -> Mapping[uuid.UUID, CatalogProduct]:
        """One batch lookup; unknown ids are absent from the result."""
        ...

    async def products_for_analytics(self) -> list[CatalogProductAnalytics]:
        """Batch lookup of products with tags for marketing analytics."""
        ...


class PaymentStarter(Protocol):
    @property
    def is_enabled(self) -> bool: ...

    async def start(self, order: Order) -> str:
        """Creates a payment for the order and returns the payment page URL."""
        ...


class OrderNotifier(Protocol):
    async def order_placed(self, order: Order, payment_url: str | None) -> None: ...


__all__ = [
    "CustomerCrmDTO",
    "OrderAnniversaryDTO",
    "OrderNotifier",
    "OrderRepository",
    "OrdersAdminGuard",
    "OrdersUnitOfWork",
    "OrdersUnitOfWorkFactory",
    "PaymentStarter",
    "ProductCatalog",
]
