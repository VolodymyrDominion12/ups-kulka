# 011 — План (Аналітика продажів, Маркетинг та CRM)

## Модулі й межі
- Згідно з `docs/УПС! Кулька — технічний план реалізації магазину.md` (розділ
  «Чиста архітектура»: для читання та звітів використовується легкий CQRS —
  query-сервіси/порти, що одразу повертають DTO) та правилами ізоляції модулів
  (`AGENTS.md`, розділ 3: модуль не читає чужі таблиці напряму):
  - Агрегації по замовленнях, каналах трафіку, клієнтах та річницях реалізуються
    всередині модуля `orders` через спеціалізований read-only порт
    `OrdersAnalyticsQueryPort` (`SqlAlchemyOrdersAnalyticsQuery`) та use cases
    `GetAnalyticsDashboard`, `ListCustomersCrm`, `GetOrderAnniversaries`.
  - Для збагачення товарної аналітики тегами (`TagGroup`) use case звертається
    до публічного фасаду `CatalogFacade.get_products_tags_summary(ids)` (1
    пакетний запит до каталогу без порушення меж модулів!).

## Індекси (використовуються індекси з міграції 0003)
| Індекс | Запит |
| --- | --- |
| `ix_orders_orders_created_at` на `orders_orders(created_at DESC)` | вибірка та агрегація замовлень за діапазоном дат `(date_from, date_to)` |
| `ix_orders_orders_status_created` на `orders_orders(status, created_at DESC)` | агрегація активних/виконаних замовлень за період |
| `ix_orders_orders_customer_phone` на `orders_orders(customer_phone, created_at DESC)` | групування клієнтів за телефоном (LTV, кількість замовлень, перша/остання покупка) |
| `ix_orders_order_items_order_id` на `orders_order_items(order_id)` | JOIN позицій замовлення для підрахунку топ товарів |

## Запити та контроль N+1
- `GetAnalyticsDashboard`: виконує фіксований набір групуючих SQL-запитів
  (`GROUP BY date`, `GROUP BY status`, `GROUP BY utm_source/order_source`,
  `GROUP BY product_id`, `GROUP BY dow/hour`) + 1 пакетний запит до
  `CatalogFacade` для підрахунку виручки за вимірами тегів (`TagGroup`).
  Кількість SQL-запитів є константною (≤ 9 запитів) і не росте зі збільшенням
  кількості замовлень у базі (перевіряється інтеграційним тестом з
  `assert_max_queries`).
- `ListCustomersCrm`: `COUNT(DISTINCT customer_phone)` + 1 `GROUP BY customer_phone`
  із пагінацією та фільтрацією = **2 запити** константно.

## API
- `GET /api/v1/admin/analytics/dashboard?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD` → `AnalyticsDashboardOut`
- `GET /api/v1/admin/analytics/customers?q=&segment=&limit=24&offset=0` → `CustomerCrmPageOut`
- `GET /api/v1/admin/analytics/anniversaries?days_ahead=14` → `list[OrderAnniversaryOut]`
- `GET /api/v1/admin/analytics/customers.csv` → `text/csv` (експорт бази для Meta Ads / розсилок)
