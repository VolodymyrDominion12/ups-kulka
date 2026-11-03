# 006 — План

## Модуль `payments`
- Домен: `Payment(id, order_id, order_number, amount: Money, provider,
  invoice_id, page_url, status, created_at, updated_at)`,
  `Payment.apply(status) -> bool` (змінилося чи ні).
- Порти: `PaymentGateway` (`create_invoice`, `fetch_status`),
  `PaymentRepository` (`add`, `get_by_invoice`, `save_status`),
  `PaymentNotifier` (повідомлення про оплату), `PaymentsUnitOfWork`.
- Use cases: `StartPayment`, `ConfirmPayment`.
- Публічний фасад `PaymentsFacade`: `is_enabled`, `start(...)` — для `orders`.
- Адаптер `MonobankGateway` (httpx): `POST /api/merchant/invoice/create`,
  `GET /api/merchant/invoice/status`, заголовок `X-Token`.
  Документація: https://monobank.ua/api-docs/acquiring

## Модель даних (міграція 0002)
- `payments_payments`: id (uuid, PK), order_id (uuid, без FK — інший модуль),
  order_number, amount_kopecks (CHECK > 0), provider, invoice_id, page_url,
  status, created_at, updated_at.

## Індекси
| Індекс | Запит |
| --- | --- |
| `UNIQUE payments_payments(invoice_id)` | вебхук: платіж за `invoiceId` |
| `payments_payments(order_id)` | статус оплати замовлення (адмінка 007, вітрина «Дякуємо») |

## API
- `POST /api/v1/payments/monobank/webhook` → 200 `{ "ok": true }`

## Налаштування
`UPS_MONOBANK_TOKEN`, `UPS_PUBLIC_BASE_URL` (для `redirectUrl` і `webHookUrl`).
