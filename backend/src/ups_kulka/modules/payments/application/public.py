"""Public facade of the payments module (used by orders)."""

from ups_kulka.modules.payments.application.dto import PaymentLinkDTO, StartPaymentCommand
from ups_kulka.modules.payments.application.use_cases.start_payment import StartPayment

__all__ = ["PaymentLinkDTO", "PaymentsFacade", "StartPaymentCommand"]


class PaymentsFacade:
    def __init__(self, start_payment: StartPayment) -> None:
        self._start_payment = start_payment

    @property
    def is_enabled(self) -> bool:
        """False until the provider token is configured: the storefront hides online payment."""
        return self._start_payment.is_enabled

    async def start(self, cmd: StartPaymentCommand) -> PaymentLinkDTO:
        return await self._start_payment(cmd)
