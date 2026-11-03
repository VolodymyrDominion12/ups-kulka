"""Admin order management use cases for salon workflow (specs/007-admin)."""

from collections.abc import Callable
from datetime import date

from ups_kulka.modules.orders.application.dto import (
    AdminOrderDTO,
    CreateAdminOrderCommand,
    GetAdminOrderQuery,
    ListAdminOrdersQuery,
    UpdateAdminOrderCommand,
)
from ups_kulka.modules.orders.application.ports import (
    OrdersAdminGuard,
    OrdersUnitOfWorkFactory,
    ProductCatalog,
)
from ups_kulka.modules.orders.application.use_cases.place_order import (
    kyiv_today,
    parse_enum,
)
from ups_kulka.modules.orders.domain.entities import (
    Customer,
    Delivery,
    DeliveryMethod,
    MarketingAttribution,
    Order,
    OrderItem,
    OrderSource,
    OrderStatus,
    PaymentMethod,
)
from ups_kulka.modules.orders.domain.errors import (
    InvalidOrder,
    OrderNotFound,
    ProductUnavailable,
)
from ups_kulka.shared.application.pagination import Page, PageRequest
from ups_kulka.shared.domain.money import Money


class ListAdminOrders:
    def __init__(
        self,
        uow_factory: OrdersUnitOfWorkFactory,
        auth: OrdersAdminGuard | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._auth = auth

    async def __call__(self, query: ListAdminOrdersQuery) -> Page[AdminOrderDTO]:
        if self._auth is not None:
            self._auth.require_admin(query.auth_token)

        page_req = PageRequest(limit=query.limit, offset=query.offset)
        async with self._uow_factory() as uow:
            page = await uow.orders.list_for_admin(
                status=query.status,
                delivery_date=query.delivery_date,
                delivery_method=query.delivery_method,
                order_source=query.order_source,
                q=query.q,
                page=page_req,
            )
        return Page(
            items=tuple(AdminOrderDTO.from_entity(o) for o in page.items),
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )


class GetAdminOrder:
    def __init__(
        self,
        uow_factory: OrdersUnitOfWorkFactory,
        auth: OrdersAdminGuard | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._auth = auth

    async def __call__(self, query: GetAdminOrderQuery) -> AdminOrderDTO:
        if self._auth is not None:
            self._auth.require_admin(query.auth_token)

        async with self._uow_factory() as uow:
            order = await uow.orders.get_by_number(query.number)
            if order is None:
                raise OrderNotFound(query.number)
        return AdminOrderDTO.from_entity(order)


class UpdateAdminOrder:
    def __init__(
        self,
        uow_factory: OrdersUnitOfWorkFactory,
        auth: OrdersAdminGuard | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._auth = auth

    async def __call__(self, cmd: UpdateAdminOrderCommand) -> AdminOrderDTO:
        if self._auth is not None:
            self._auth.require_admin(cmd.auth_token)

        new_status: OrderStatus | None = None
        if cmd.status is not None:
            try:
                new_status = OrderStatus(cmd.status)
            except ValueError as exc:
                raise InvalidOrder(f"Невідомий статус замовлення: {cmd.status}") from exc

        async with self._uow_factory() as uow:
            order = await uow.orders.get_by_number(cmd.number)
            if order is None:
                raise OrderNotFound(cmd.number)

            new_entry = None
            if new_status is not None:
                new_entry = order.change_status(new_status, note=cmd.status_note)

            order.update_salon_details(
                internal_note=cmd.internal_note,
                delivery_date=cmd.delivery_date,
                time_slot=cmd.time_slot,
                address=cmd.address,
            )
            await uow.orders.save(order, new_entry)
            await uow.commit()

        return AdminOrderDTO.from_entity(order)


class CreateAdminOrder:
    """Quick order entry in the salon for Instagram/Telegram/Phone/Walk-in customers."""

    def __init__(
        self,
        uow_factory: OrdersUnitOfWorkFactory,
        catalog: ProductCatalog,
        auth: OrdersAdminGuard | None = None,
        today: Callable[[], date] = kyiv_today,
    ) -> None:
        self._uow_factory = uow_factory
        self._catalog = catalog
        self._auth = auth
        self._today = today

    async def __call__(self, cmd: CreateAdminOrderCommand) -> AdminOrderDTO:
        if self._auth is not None:
            self._auth.require_admin(cmd.auth_token)

        customer = Customer.create(name=cmd.customer_name, phone=cmd.phone, comment=cmd.comment)
        delivery = Delivery.create(
            method=parse_enum(DeliveryMethod, cmd.delivery_method, "спосіб отримання"),
            today=self._today(),
            address=cmd.address,
            on_date=cmd.delivery_date,
            time_slot=cmd.time_slot,
        )
        payment_method = parse_enum(PaymentMethod, cmd.payment_method, "спосіб оплати")
        order_source = parse_enum(OrderSource, cmd.order_source, "канал замовлення")

        products = await self._catalog.products_for_order([line.product_id for line in cmd.lines])
        missing = [line.product_id for line in cmd.lines if line.product_id not in products]
        if missing:
            raise ProductUnavailable(list(dict.fromkeys(missing)))

        marketing = MarketingAttribution.create(
            order_source=order_source,
            promo_code=cmd.promo_code,
            discount_kopecks=cmd.discount_kopecks,
        )
        order = Order.place(
            customer=customer,
            delivery=delivery,
            payment_method=payment_method,
            marketing=marketing,
            internal_note=cmd.internal_note,
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

        return AdminOrderDTO.from_entity(order)
