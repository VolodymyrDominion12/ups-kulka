# 008 — План

## Модуль `notifications`
- Без таблиць і без HTTP (presentation порожній).
- Application: DTO `OrderPlacedNotice`, `PaymentReceivedNotice`; use cases
  `NotifyOrderPlaced`, `NotifyPaymentReceived` формують текст українською;
  порт `MessageSender.send(text)`.
- Фасад `NotificationsFacade` — для `orders` і `payments`.
- Infrastructure: `TelegramSender` (httpx, `sendMessage`), `LogSender`.
- DI: `TelegramSender`, якщо задані токен і chat_id, інакше `LogSender`.

## Налаштування
`UPS_TELEGRAM_BOT_TOKEN`, `UPS_TELEGRAM_CHAT_ID`.
