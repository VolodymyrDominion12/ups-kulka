"""N+1 guard for checkout (specs/004-checkout/plan.md): query count does not grow with items."""

import uuid

import pytest
from dependency_injector import providers

from tests.conftest import QueryCounter
from tests.fakes.orders import RecordingSender
from ups_kulka.container import Container
from ups_kulka.modules.catalog.application.dto import CreateProductCommand
from ups_kulka.modules.orders.application.dto import OrderLineInput, PlaceOrderCommand

pytestmark = pytest.mark.integration

# catalog: SELECT prices (+ BEGIN/ROLLBACK noise);
# orders: INSERT order RETURNING number + batch INSERT items + batch INSERT history.
PLACE_ORDER_QUERIES = 7


async def _products(container: Container, count: int) -> list[uuid.UUID]:
    create_product = container.catalog.create_product()
    ids = []
    for i in range(count):
        dto = await create_product(
            CreateProductCommand(
                slug=f"product-{i}", name=f"Product {i}", description="", price_kopecks=10000
            )
        )
        ids.append(dto.id)
    return ids


@pytest.mark.parametrize("items", [1, 30])
async def test_place_order_query_count_is_constant(
    container: Container, query_counter: QueryCounter, items: int
) -> None:
    container.notifications.sender.override(providers.Object(RecordingSender()))
    product_ids = await _products(container, items)
    place_order = container.orders.place_order()
    command = PlaceOrderCommand(
        customer_name="Олена",
        phone="0931112233",
        delivery_method="pickup",
        payment_method="on_delivery",
        lines=tuple(OrderLineInput(pid, 2) for pid in product_ids),
    )

    with query_counter.assert_max_queries(PLACE_ORDER_QUERIES):
        placed = await place_order(command)

    assert len(placed.items) == items
    assert placed.total_kopecks == items * 2 * 10000
