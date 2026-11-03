"""Orders HTTP adapter (thin, see backend/AGENTS.md)."""

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from ups_kulka.modules.orders.application.use_cases.get_checkout_options import (
    GetCheckoutOptions,
)
from ups_kulka.modules.orders.application.use_cases.place_order import PlaceOrder
from ups_kulka.modules.orders.presentation.schemas import (
    CheckoutOptionsOut,
    PlacedOrderOut,
    PlaceOrderIn,
)
from ups_kulka.shared.presentation.errors import ErrorOut

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.get("/checkout-options")
@inject
async def checkout_options(
    use_case: GetCheckoutOptions = Depends(Provide["orders.get_checkout_options"]),
) -> CheckoutOptionsOut:
    return CheckoutOptionsOut.from_dto(await use_case())


@router.post("", status_code=status.HTTP_201_CREATED, responses={422: {"model": ErrorOut}})
@inject
async def place_order(
    body: PlaceOrderIn,
    use_case: PlaceOrder = Depends(Provide["orders.place_order"]),
) -> PlacedOrderOut:
    return PlacedOrderOut.from_dto(await use_case(body.to_command()))
