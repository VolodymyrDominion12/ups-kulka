import uuid
from collections.abc import Callable, Mapping, Sequence
from typing import Protocol

from ups_kulka.modules.orders.application.dto import CatalogProduct
from ups_kulka.modules.orders.domain.entities import Order
from ups_kulka.shared.application.uow import UnitOfWork


class OrderRepository(Protocol):
    async def add(self, order: Order) -> int:
        """Saves the order with its items (constant number of queries); returns its number."""
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


class PaymentStarter(Protocol):
    @property
    def is_enabled(self) -> bool: ...

    async def start(self, order: Order) -> str:
        """Creates a payment for the order and returns the payment page URL."""
        ...


class OrderNotifier(Protocol):
    async def order_placed(self, order: Order, payment_url: str | None) -> None: ...
