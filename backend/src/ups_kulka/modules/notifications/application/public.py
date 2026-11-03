"""Public facade of the notifications module (used by orders and payments)."""

from ups_kulka.modules.notifications.application.dto import (
    NoticeLine,
    OrderPlacedNotice,
    PaymentReceivedNotice,
)
from ups_kulka.modules.notifications.application.use_cases.notify_shop import (
    NotifyOrderPlaced,
    NotifyPaymentReceived,
)

__all__ = ["NoticeLine", "NotificationsFacade", "OrderPlacedNotice", "PaymentReceivedNotice"]


class NotificationsFacade:
    def __init__(
        self, order_placed: NotifyOrderPlaced, payment_received: NotifyPaymentReceived
    ) -> None:
        self._order_placed = order_placed
        self._payment_received = payment_received

    async def order_placed(self, notice: OrderPlacedNotice) -> None:
        await self._order_placed(notice)

    async def payment_received(self, notice: PaymentReceivedNotice) -> None:
        await self._payment_received(notice)
