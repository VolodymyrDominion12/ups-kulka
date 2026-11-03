from ups_kulka.modules.orders.application.dto import CheckoutOptionsDTO
from ups_kulka.modules.orders.application.ports import PaymentStarter
from ups_kulka.modules.orders.domain.entities import DeliveryMethod, PaymentMethod


class GetCheckoutOptions:
    """What the storefront may offer: online payment only when it is configured."""

    def __init__(self, payments: PaymentStarter) -> None:
        self._payments = payments

    async def __call__(self) -> CheckoutOptionsDTO:
        payment_methods = [PaymentMethod.ON_DELIVERY]
        if self._payments.is_enabled:
            payment_methods.append(PaymentMethod.ONLINE)
        return CheckoutOptionsDTO(
            delivery_methods=tuple(m.value for m in DeliveryMethod),
            payment_methods=tuple(m.value for m in payment_methods),
        )
