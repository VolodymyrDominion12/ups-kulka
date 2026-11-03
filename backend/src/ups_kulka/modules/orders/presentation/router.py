"""Orders HTTP adapter (thin, see backend/AGENTS.md)."""

import datetime as dt
from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, Query, status

from ups_kulka.modules.orders.application.dto import (
    AnalyticsDashboardQuery,
    GetAdminOrderQuery,
    ListAdminOrdersQuery,
    ListCustomersCrmQuery,
)
from ups_kulka.modules.orders.application.use_cases.admin_orders import (
    CreateAdminOrder,
    GetAdminOrder,
    ListAdminOrders,
    UpdateAdminOrder,
)
from ups_kulka.modules.orders.application.use_cases.analytics import (
    GetAnalyticsDashboard,
    GetOrderAnniversaries,
    ListCustomersCrm,
)
from ups_kulka.modules.orders.application.use_cases.get_checkout_options import (
    GetCheckoutOptions,
)
from ups_kulka.modules.orders.application.use_cases.place_order import PlaceOrder
from ups_kulka.modules.orders.presentation.schemas import (
    AdminOrderOut,
    AdminOrderPageOut,
    AnalyticsDashboardOut,
    CheckoutOptionsOut,
    CreateAdminOrderIn,
    CustomerCrmPageOut,
    OrderAnniversaryOut,
    PlacedOrderOut,
    PlaceOrderIn,
    UpdateAdminOrderIn,
)
from ups_kulka.shared.application.pagination import DEFAULT_LIMIT, MAX_LIMIT
from ups_kulka.shared.presentation.errors import ErrorOut

router = APIRouter(tags=["orders"])

_ERRORS: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorOut},
    404: {"model": ErrorOut},
    422: {"model": ErrorOut},
}


@router.get("/api/v1/orders/checkout-options")
@inject
async def checkout_options(
    use_case: GetCheckoutOptions = Depends(Provide["orders.get_checkout_options"]),
) -> CheckoutOptionsOut:
    return CheckoutOptionsOut.from_dto(await use_case())


@router.post(
    "/api/v1/orders",
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorOut}},
)
@inject
async def place_order(
    body: PlaceOrderIn,
    use_case: PlaceOrder = Depends(Provide["orders.place_order"]),
) -> PlacedOrderOut:
    return PlacedOrderOut.from_dto(await use_case(body.to_command()))


@router.get("/api/v1/admin/orders", responses=_ERRORS, tags=["admin-orders"])
@inject
async def list_admin_orders(
    status_filter: Annotated[str | None, Query(alias="status", max_length=16)] = None,
    delivery_date: dt.date | None = None,
    delivery_method: Annotated[str | None, Query(max_length=16)] = None,
    order_source: Annotated[str | None, Query(max_length=32)] = None,
    q: Annotated[str | None, Query(max_length=120)] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    authorization: Annotated[str | None, Header()] = None,
    use_case: ListAdminOrders = Depends(Provide["orders.list_admin_orders"]),
) -> AdminOrderPageOut:
    query = ListAdminOrdersQuery(
        status=status_filter,
        delivery_date=delivery_date,
        delivery_method=delivery_method,
        order_source=order_source,
        q=q,
        limit=limit,
        offset=offset,
        auth_token=authorization,
    )
    return AdminOrderPageOut.from_page(await use_case(query))


@router.post(
    "/api/v1/admin/orders",
    status_code=status.HTTP_201_CREATED,
    responses=_ERRORS,
    tags=["admin-orders"],
)
@inject
async def create_admin_order(
    body: CreateAdminOrderIn,
    authorization: Annotated[str | None, Header()] = None,
    use_case: CreateAdminOrder = Depends(Provide["orders.create_admin_order"]),
) -> AdminOrderOut:
    return AdminOrderOut.from_dto(await use_case(body.to_command(authorization)))


@router.get("/api/v1/admin/orders/{number}", responses=_ERRORS, tags=["admin-orders"])
@inject
async def get_admin_order(
    number: int,
    authorization: Annotated[str | None, Header()] = None,
    use_case: GetAdminOrder = Depends(Provide["orders.get_admin_order"]),
) -> AdminOrderOut:
    return AdminOrderOut.from_dto(
        await use_case(GetAdminOrderQuery(number=number, auth_token=authorization))
    )


@router.patch("/api/v1/admin/orders/{number}", responses=_ERRORS, tags=["admin-orders"])
@inject
async def update_admin_order(
    number: int,
    body: UpdateAdminOrderIn,
    authorization: Annotated[str | None, Header()] = None,
    use_case: UpdateAdminOrder = Depends(Provide["orders.update_admin_order"]),
) -> AdminOrderOut:
    return AdminOrderOut.from_dto(await use_case(body.to_command(number, authorization)))


@router.get(
    "/api/v1/admin/analytics/dashboard",
    responses=_ERRORS,
    tags=["admin-analytics"],
)
@inject
async def get_analytics_dashboard(
    date_from: dt.date | None = None,
    date_to: dt.date | None = None,
    authorization: Annotated[str | None, Header()] = None,
    use_case: GetAnalyticsDashboard = Depends(Provide["orders.get_analytics_dashboard"]),
) -> AnalyticsDashboardOut:
    query = AnalyticsDashboardQuery(
        date_from=date_from,
        date_to=date_to,
        auth_token=authorization,
    )
    return AnalyticsDashboardOut.from_dto(await use_case(query))


@router.get(
    "/api/v1/admin/analytics/customers",
    responses=_ERRORS,
    tags=["admin-analytics"],
)
@inject
async def list_customers_crm(
    q: Annotated[str | None, Query(max_length=120)] = None,
    segment: Annotated[str | None, Query(max_length=32)] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    authorization: Annotated[str | None, Header()] = None,
    use_case: ListCustomersCrm = Depends(Provide["orders.list_customers_crm"]),
) -> CustomerCrmPageOut:
    query = ListCustomersCrmQuery(
        q=q,
        segment=segment,
        limit=limit,
        offset=offset,
        auth_token=authorization,
    )
    return CustomerCrmPageOut.from_page(await use_case(query))


@router.get(
    "/api/v1/admin/analytics/anniversaries",
    responses=_ERRORS,
    tags=["admin-analytics"],
)
@inject
async def get_order_anniversaries(
    days_ahead: Annotated[int, Query(ge=1, le=60)] = 14,
    authorization: Annotated[str | None, Header()] = None,
    use_case: GetOrderAnniversaries = Depends(Provide["orders.get_order_anniversaries"]),
) -> list[OrderAnniversaryOut]:
    rows = await use_case(days_ahead=days_ahead, auth_token=authorization)
    return [OrderAnniversaryOut.from_dto(r) for r in rows]
