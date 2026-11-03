# 004 — План

## Модулі й межі
- `orders` — агрегат `Order`, use cases `PlaceOrder`, `GetCheckoutOptions`.
- Інші модулі — лише через `application.public`:
  - `catalog.application.public.CatalogFacade.products_for_order(ids)` — ціни;
  - `payments.application.public.PaymentsFacade` — чи ввімкнена оплата, старт платежу;
  - `notifications.application.public.NotificationsFacade` — повідомлення власнику.
- Адаптери до фасадів — у `orders/infrastructure/adapters.py`; порти —
  у `orders/application/ports.py`. Контейнер `orders` отримує фасади як
  залежності з кореневого `container.py`.

## Домен
- `PhoneNumber` (нормалізація до `+380XXXXXXXXX`), `Customer`,
  `Delivery(method: pickup|taxi, address, date, time_slot)`,
  `OrderItem(product_id, name, unit_price: Money, quantity)`,
  `Order.place(...)` — зливає дублікати, перевіряє ліміти, `total`.
- `PaymentMethod`: `on_delivery | online`. `OrderStatus`: `new` (решта — в 007).

## Модель даних (міграція 0002)
- `orders_orders`: id (uuid, PK), number (int, IDENTITY з 1001, UNIQUE),
  status, customer_name, customer_phone, comment, delivery_method,
  delivery_address, delivery_date (date), delivery_slot, payment_method,
  total_kopecks (CHECK ≥ 0), created_at (timestamptz).
- `orders_order_items`: id (uuid, PK), order_id (FK → orders_orders, CASCADE),
  product_id (uuid, без FK: таблиця іншого модуля), product_name,
  unit_price_kopecks, quantity (CHECK 1–99).

## Індекси (і для яких запитів)
| Індекс | Запит |
| --- | --- |
| `UNIQUE orders_orders(number)` | пошук замовлення за номером (адмінка, Telegram) |
| `orders_order_items(order_id)` | позиції замовлення (FK) |
Списків замовлень поки немає; індекс `(status, created_at)` додасть 007-admin.

## Запити
- `PlaceOrder`: 1 запит до каталогу (`WHERE id IN (...)`, `selectinload` не
  потрібен) + INSERT замовлення + один пакетний INSERT позицій. Кількість
  запитів не залежить від кількості позицій (`test_orders_queries.py`).

## API
- `GET /api/v1/orders/checkout-options` → `{delivery_methods, payment_methods}`
- `POST /api/v1/orders` → 201 `PlacedOrderOut` (`number`, `total_kopecks`,
  `payment_url | null`, позиції)
