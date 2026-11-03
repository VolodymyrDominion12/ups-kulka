from ups_kulka.shared.domain.errors import NotFoundError, ValidationError


class InvalidPayment(ValidationError):
    code = "invalid_payment"


class OnlinePaymentUnavailable(ValidationError):
    code = "online_payment_unavailable"

    def __init__(self) -> None:
        super().__init__("Онлайн-оплата поки недоступна. Оберіть оплату при отриманні.")


class PaymentsDisabled(NotFoundError):
    code = "payments_disabled"

    def __init__(self) -> None:
        super().__init__("Online payments are not configured")


class PaymentNotFound(NotFoundError):
    code = "payment_not_found"

    def __init__(self, invoice_id: str) -> None:
        super().__init__(f"Payment for invoice '{invoice_id}' not found")
