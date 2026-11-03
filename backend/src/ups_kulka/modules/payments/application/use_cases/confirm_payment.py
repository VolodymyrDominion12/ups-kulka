import logging

from ups_kulka.modules.payments.application.ports import (
    PaymentGateway,
    PaymentNotifier,
    PaymentsUnitOfWorkFactory,
)
from ups_kulka.modules.payments.domain.errors import PaymentNotFound, PaymentsDisabled

logger = logging.getLogger("ups_kulka.payments")


class ConfirmPayment:
    """Handles a provider webhook.

    The webhook body is NOT trusted: only its invoice id is used, the status is
    re-read from the provider with our own token. Repeated webhooks are no-ops.
    """

    def __init__(
        self,
        uow_factory: PaymentsUnitOfWorkFactory,
        gateway: PaymentGateway | None,
        notifier: PaymentNotifier,
    ) -> None:
        self._uow_factory = uow_factory
        self._gateway = gateway
        self._notifier = notifier

    async def __call__(self, invoice_id: str) -> None:
        if self._gateway is None:
            raise PaymentsDisabled
        async with self._uow_factory() as uow:
            if await uow.payments.get_by_invoice(invoice_id) is None:
                raise PaymentNotFound(invoice_id)  # do not call the bank for unknown ids

        status = await self._gateway.fetch_status(invoice_id)

        async with self._uow_factory() as uow:
            payment = await uow.payments.get_by_invoice(invoice_id, for_update=True)
            if payment is None:
                raise PaymentNotFound(invoice_id)
            was_paid = payment.is_paid
            if not payment.apply(status):
                return
            await uow.payments.save(payment)
            await uow.commit()

        if payment.is_paid and not was_paid:
            try:
                await self._notifier.payment_received(
                    order_number=payment.order_number, amount_kopecks=payment.amount.kopecks
                )
            except Exception:  # the payment is saved; a lost message must not fail the webhook
                logger.exception("payment notification failed for order %s", payment.order_number)
