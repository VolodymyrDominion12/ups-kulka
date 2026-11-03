import logging
from collections.abc import Callable
from datetime import date, datetime
from zoneinfo import ZoneInfo

from ups_kulka.modules.orders.application.dto import PlacedOrderDTO, PlaceOrderCommand
from ups_kulka.modules.orders.application.ports import (
    OrderNotifier,
    OrdersUnitOfWorkFactory,
    PaymentStarter,
    ProductCatalog,
)
from ups_kulka.modules.orders.domain.entities import (
    Customer,
    Delivery,
    DeliveryMethod,
    Order,
    OrderItem,
    PaymentMethod,
)
from ups_kulka.modules.orders.domain.errors import (
    InvalidOrder,
    OnlinePaymentUnavailable,
    ProductUnavailable,
)
from ups_kulka.shared.domain.money import Money

logger = logging.getLogger("ups_kulka.orders")

KYIV = ZoneInfo("Europe/Kyiv")


def kyiv_today() -> date:
    return datetime.now(KYIV).date()


class PlaceOrder:
    """Prices come from the catalogue only; the client never sends a price."""

    def __init__(
        self,
        uow_factory: OrdersUnitOfWorkFactory,
        catalog: ProductCatalog,
        payments: PaymentStarter,
        notifier: OrderNotifier,
        today: Callable[[], date] = kyiv_today,
    ) -> None:
        self._uow_factory = uow_factory
        self._catalog = catalog
        self._payments = payments
        self._notifier = notifier
        self._today = today

    async def __call__(self, cmd: PlaceOrderCommand) -> PlacedOrderDTO:
        customer = Customer.create(name=cmd.customer_name, phone=cmd.phone, comment=cmd.comment)
        delivery = Delivery.create(
            method=_parse(DeliveryMethod, cmd.delivery_method, "спосіб отримання"),
            today=self._today(),
            address=cmd.address,
            on_date=cmd.delivery_date,
            time_slot=cmd.time_slot,
        )
        payment_method = _parse(PaymentMethod, cmd.payment_method, "спосіб оплати")
        if payment_method is PaymentMethod.ONLINE and not self._payments.is_enabled:
            raise OnlinePaymentUnavailable

        products = await self._catalog.products_for_order([line.product_id for line in cmd.lines])
        unavailable = [
            line.product_id
            for line in cmd.lines
            if line.product_id not in products or not products[line.product_id].is_active
        ]
        if unavailable:
            raise ProductUnavailable(list(dict.fromkeys(unavailable)))

        order = Order.place(
            customer=customer,
            delivery=delivery,
            payment_method=payment_method,
            items=[
                OrderItem(
                    product_id=line.product_id,
                    product_name=products[line.product_id].name,
                    unit_price=Money(products[line.product_id].price_kopecks),
                    quantity=line.quantity,
                )
                for line in cmd.lines
            ],
        )
        async with self._uow_factory() as uow:
            order.assign_number(await uow.orders.add(order))
            await uow.commit()

        payment_url = await self._start_payment(order)
        await self._notify(order, payment_url)
        return PlacedOrderDTO.from_entity(order, payment_url)

    async def _start_payment(self, order: Order) -> str | None:
        if order.payment_method is not PaymentMethod.ONLINE:
            return None
        try:
            return await self._payments.start(order)
        except Exception:  # the order is saved; the manager agrees on payment by phone
            logger.exception("could not start payment for order %s", order.number)
            return None

    async def _notify(self, order: Order, payment_url: str | None) -> None:
        try:
            await self._notifier.order_placed(order, payment_url)
        except Exception:  # a lost message must not lose the order
            logger.exception("order notification failed for order %s", order.number)


def _parse[E: (DeliveryMethod, PaymentMethod)](enum: type[E], value: str, what: str) -> E:
    try:
        return enum(value)
    except ValueError as exc:
        raise InvalidOrder(f"Невідомий {what}: {value}") from exc
