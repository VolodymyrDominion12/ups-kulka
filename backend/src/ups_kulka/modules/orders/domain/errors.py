import uuid

from ups_kulka.shared.domain.errors import ValidationError


class InvalidPhone(ValidationError):
    code = "invalid_phone"

    def __init__(self) -> None:
        super().__init__("Вкажіть номер у форматі 093 123 45 67 або +380931234567")


class AddressRequired(ValidationError):
    code = "address_required"

    def __init__(self) -> None:
        super().__init__("Для доставки таксі вкажіть адресу")


class DeliveryDateInPast(ValidationError):
    code = "delivery_date_in_past"

    def __init__(self) -> None:
        super().__init__("Дата доставки не може бути в минулому")


class InvalidOrder(ValidationError):
    code = "invalid_order"


class ProductUnavailable(ValidationError):
    code = "product_unavailable"

    def __init__(self, product_ids: list[uuid.UUID]) -> None:
        super().__init__("Деяких товарів уже немає в каталозі. Оновіть кошик.")
        self.product_ids = product_ids


class OnlinePaymentUnavailable(ValidationError):
    code = "online_payment_unavailable"

    def __init__(self) -> None:
        super().__init__("Онлайн-оплата поки недоступна. Оберіть оплату при отриманні.")
