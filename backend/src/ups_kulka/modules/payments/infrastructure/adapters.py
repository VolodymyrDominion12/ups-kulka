"""Adapters from payments ports to other modules' public facades."""

from ups_kulka.modules.notifications.application.public import (
    NotificationsFacade,
    PaymentReceivedNotice,
)


class NotificationsPaymentNotifier:
    def __init__(self, notifications: NotificationsFacade) -> None:
        self._notifications = notifications

    async def payment_received(self, *, order_number: int, amount_kopecks: int) -> None:
        await self._notifications.payment_received(
            PaymentReceivedNotice(order_number=order_number, amount_kopecks=amount_kopecks)
        )
