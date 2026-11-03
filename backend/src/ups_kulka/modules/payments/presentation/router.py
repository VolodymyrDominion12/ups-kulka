"""Payments HTTP adapter (thin, see backend/AGENTS.md)."""

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from ups_kulka.modules.payments.application.use_cases.confirm_payment import ConfirmPayment
from ups_kulka.modules.payments.presentation.schemas import MonobankWebhookIn, WebhookAckOut
from ups_kulka.shared.presentation.errors import ErrorOut

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("/monobank/webhook", responses={404: {"model": ErrorOut}})
@inject
async def monobank_webhook(
    body: MonobankWebhookIn,
    use_case: ConfirmPayment = Depends(Provide["payments.confirm_payment"]),
) -> WebhookAckOut:
    await use_case(body.invoice_id)
    return WebhookAckOut()
