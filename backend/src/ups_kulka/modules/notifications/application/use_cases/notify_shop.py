from ups_kulka.modules.notifications.application.dto import (
    OrderPlacedNotice,
    PaymentReceivedNotice,
)
from ups_kulka.modules.notifications.application.messages import (
    order_placed_text,
    payment_received_text,
)
from ups_kulka.modules.notifications.application.ports import MessageSender


class NotifyOrderPlaced:
    def __init__(self, sender: MessageSender) -> None:
        self._sender = sender

    async def __call__(self, notice: OrderPlacedNotice) -> None:
        await self._sender.send(order_placed_text(notice))


class NotifyPaymentReceived:
    def __init__(self, sender: MessageSender) -> None:
        self._sender = sender

    async def __call__(self, notice: PaymentReceivedNotice) -> None:
        await self._sender.send(payment_received_text(notice))
