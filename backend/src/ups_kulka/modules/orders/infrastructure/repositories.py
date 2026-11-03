import uuid

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ups_kulka.modules.orders.domain.entities import Order
from ups_kulka.modules.orders.infrastructure.tables import OrderItemRow, OrderRow


class SqlAlchemyOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, order: Order) -> int:
        """2 statements for any number of items: INSERT order RETURNING number + batch INSERT."""
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
            total_kopecks=order.total.kopecks,
            created_at=order.created_at,
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
        return row.number
