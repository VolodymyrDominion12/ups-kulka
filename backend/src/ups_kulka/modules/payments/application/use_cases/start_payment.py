from ups_kulka.modules.payments.application.dto import PaymentLinkDTO, StartPaymentCommand
from ups_kulka.modules.payments.application.ports import (
    PaymentGateway,
    PaymentsUnitOfWorkFactory,
)
from ups_kulka.modules.payments.domain.entities import Payment
from ups_kulka.modules.payments.domain.errors import OnlinePaymentUnavailable
from ups_kulka.shared.domain.money import Money


class StartPayment:
    """Creates an invoice at the provider and stores the payment."""

    def __init__(
        self, uow_factory: PaymentsUnitOfWorkFactory, gateway: PaymentGateway | None
    ) -> None:
        self._uow_factory = uow_factory
        self._gateway = gateway

    @property
    def is_enabled(self) -> bool:
        return self._gateway is not None

    async def __call__(self, cmd: StartPaymentCommand) -> PaymentLinkDTO:
        if self._gateway is None:
            raise OnlinePaymentUnavailable
        payment = Payment.create(
            order_id=cmd.order_id,
            order_number=cmd.order_number,
            amount=Money(cmd.amount_kopecks),
            provider=self._gateway.provider,
        )
        # The network call happens before the transaction, so no DB lock waits on the bank.
        invoice = await self._gateway.create_invoice(payment, cmd.description)
        payment.attach_invoice(invoice.invoice_id, invoice.page_url)

        async with self._uow_factory() as uow:
            await uow.payments.add(payment)
            await uow.commit()
        return PaymentLinkDTO(payment_id=payment.id, page_url=invoice.page_url)
