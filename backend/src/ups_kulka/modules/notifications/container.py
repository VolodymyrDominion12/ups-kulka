from dependency_injector import containers, providers

from ups_kulka.modules.notifications.application.public import NotificationsFacade
from ups_kulka.modules.notifications.application.use_cases.notify_shop import (
    NotifyOrderPlaced,
    NotifyPaymentReceived,
)
from ups_kulka.modules.notifications.infrastructure.senders import make_sender


class NotificationsContainer(containers.DeclarativeContainer):
    telegram_bot_token = providers.Dependency(instance_of=str, default="")
    telegram_chat_id = providers.Dependency(instance_of=str, default="")

    sender = providers.Singleton(
        make_sender, bot_token=telegram_bot_token, chat_id=telegram_chat_id
    )
    notify_order_placed = providers.Factory(NotifyOrderPlaced, sender=sender)
    notify_payment_received = providers.Factory(NotifyPaymentReceived, sender=sender)

    facade = providers.Factory(
        NotificationsFacade,
        order_placed=notify_order_placed,
        payment_received=notify_payment_received,
    )
