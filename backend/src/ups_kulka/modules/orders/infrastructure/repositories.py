import uuid
from datetime import date

from sqlalchemy import ColumnElement, func, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ups_kulka.modules.orders.domain.entities import (
    Customer,
    Delivery,
    DeliveryMethod,
    MarketingAttribution,
    Order,
    OrderItem,
    OrderSource,
    OrderStatus,
    OrderStatusEntry,
    PaymentMethod,
    PhoneNumber,
)
from ups_kulka.modules.orders.infrastructure.tables import (
    OrderItemRow,
    OrderRow,
    OrderStatusHistoryRow,
)
from ups_kulka.shared.application.pagination import Page, PageRequest
from ups_kulka.shared.domain.money import Money


def order_to_domain(row: OrderRow, *, include_history: bool = True) -> Order:
    history: tuple[OrderStatusEntry, ...] = ()
    if include_history:
        history = tuple(
            OrderStatusEntry(
                id=h.id,
                from_status=OrderStatus(h.from_status) if h.from_status else None,
                to_status=OrderStatus(h.to_status),
                note=h.note,
                changed_at=h.changed_at,
            )
            for h in sorted(row.status_history, key=lambda item: item.changed_at)
        )
    return Order(
        id=row.id,
        number=row.number,
        status=OrderStatus(row.status),
        customer=Customer(
            name=row.customer_name,
            phone=PhoneNumber(row.customer_phone),
            comment=row.comment,
        ),
        delivery=Delivery(
            method=DeliveryMethod(row.delivery_method),
            address=row.delivery_address,
            date=row.delivery_date,
            time_slot=row.delivery_slot,
        ),
        items=tuple(
            OrderItem(
                product_id=item.product_id,
                product_name=item.product_name,
                unit_price=Money(item.unit_price_kopecks),
                quantity=item.quantity,
            )
            for item in row.items
        ),
        payment_method=PaymentMethod(row.payment_method),
        marketing=MarketingAttribution(
            order_source=OrderSource(row.order_source),
            utm_source=row.utm_source,
            utm_medium=row.utm_medium,
            utm_campaign=row.utm_campaign,
            landing_page=row.landing_page,
            promo_code=row.promo_code,
            discount_kopecks=row.discount_kopecks,
        ),
        internal_note=row.internal_note,
        created_at=row.created_at,
        updated_at=row.updated_at,
        status_history=history,
    )


class SqlAlchemyOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, order: Order) -> int:
        """Constant statements: INSERT order + batch INSERT items + batch INSERT history."""
        row = OrderRow(
            id=order.id,
            status=order.status.value,
            customer_name=order.customer.name,
            customer_phone=order.customer.phone.value,
            comment=order.customer.comment,
            delivery_method=order.delivery.method.value,
            delivery_address=order.delivery.address,
            delivery_date=order.delivery.date,
            delivery_slot=order.delivery.time_slot,
            payment_method=order.payment_method.value,
            order_source=order.marketing.order_source.value,
            utm_source=order.marketing.utm_source,
            utm_medium=order.marketing.utm_medium,
            utm_campaign=order.marketing.utm_campaign,
            landing_page=order.marketing.landing_page,
            promo_code=order.marketing.promo_code,
            discount_kopecks=order.marketing.discount_kopecks,
            total_kopecks=order.total.kopecks,
            internal_note=order.internal_note,
            created_at=order.created_at,
            updated_at=order.updated_at or order.created_at,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.execute(
            insert(OrderItemRow),
            [
                {
                    "id": uuid.uuid4(),
                    "order_id": order.id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "unit_price_kopecks": item.unit_price.kopecks,
                    "quantity": item.quantity,
                }
                for item in order.items
            ],
        )
        if order.status_history:
            await self._session.execute(
                insert(OrderStatusHistoryRow),
                [
                    {
                        "id": entry.id,
                        "order_id": order.id,
                        "from_status": entry.from_status.value if entry.from_status else None,
                        "to_status": entry.to_status.value,
                        "note": entry.note,
                        "changed_at": entry.changed_at,
                    }
                    for entry in order.status_history
                ],
            )
        return row.number

    async def get_by_number(self, number: int) -> Order | None:
        stmt = (
            select(OrderRow)
            .options(
                selectinload(OrderRow.items),
                selectinload(OrderRow.status_history),
            )
            .where(OrderRow.number == number)
        )
        row = await self._session.scalar(stmt)
        return order_to_domain(row, include_history=True) if row is not None else None

    async def save(self, order: Order, new_status_entry: OrderStatusEntry | None) -> None:
        await self._session.execute(
            update(OrderRow)
            .where(OrderRow.id == order.id)
            .values(
                status=order.status.value,
                delivery_address=order.delivery.address,
                delivery_date=order.delivery.date,
                delivery_slot=order.delivery.time_slot,
                internal_note=order.internal_note,
                updated_at=order.updated_at or order.created_at,
            )
        )
        if new_status_entry is not None:
            await self._session.execute(
                insert(OrderStatusHistoryRow),
                [
                    {
                        "id": new_status_entry.id,
                        "order_id": order.id,
                        "from_status": (
                            new_status_entry.from_status.value
                            if new_status_entry.from_status
                            else None
                        ),
                        "to_status": new_status_entry.to_status.value,
                        "note": new_status_entry.note,
                        "changed_at": new_status_entry.changed_at,
                    }
                ],
            )

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
        conditions: list[ColumnElement[bool]] = []
        if status:
            conditions.append(OrderRow.status == status)
        if delivery_date is not None:
            conditions.append(OrderRow.delivery_date == delivery_date)
        if delivery_method:
            conditions.append(OrderRow.delivery_method == delivery_method)
        if order_source:
            conditions.append(OrderRow.order_source == order_source)
        if q and q.strip():
            clean_q = q.strip()
            pattern = f"%{clean_q}%"
            clauses: list[ColumnElement[bool]] = [
                OrderRow.customer_name.ilike(pattern),
                OrderRow.customer_phone.ilike(pattern),
            ]
            if clean_q.isdigit():
                clauses.append(OrderRow.number == int(clean_q))
            conditions.append(or_(*clauses))

        total = await self._session.scalar(
            select(func.count()).select_from(OrderRow).where(*conditions)
        )
        rows = await self._session.scalars(
            select(OrderRow)
            .options(
                selectinload(OrderRow.items),
                selectinload(OrderRow.status_history),
            )
            .where(*conditions)
            .order_by(OrderRow.created_at.desc(), OrderRow.number.desc())
            .limit(page.limit)
            .offset(page.offset)
        )
        return Page(
            items=tuple(order_to_domain(row, include_history=True) for row in rows),
            total=total or 0,
            limit=page.limit,
            offset=page.offset,
        )

    async def list_all_for_analytics(self) -> list[Order]:
        rows = await self._session.scalars(
            select(OrderRow)
            .options(selectinload(OrderRow.items))
            .order_by(OrderRow.created_at.desc())
        )
        return [order_to_domain(row, include_history=False) for row in rows]
