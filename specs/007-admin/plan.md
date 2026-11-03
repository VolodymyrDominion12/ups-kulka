# 007 — План (Мобільна адмін-панель)

## Модулі й межі
1. **Новий модуль `ups_kulka.modules.admin_auth`**:
   - Відповідає за перевірку пароля адміністратора та випуск/валідацію
     підписаного токена сесії (HMAC-SHA256 на базі `settings.admin_secret_key`
     та `settings.admin_password`).
   - Оскільки роль одна (`admin`), таблиця користувачів у БД не потрібна:
     пароль і секрет задаються змінними середовища `UPS_ADMIN_PASSWORD` та
     `UPS_ADMIN_SECRET_KEY`.
   - Use cases: `LoginAdmin`, `VerifyAdminToken`.
2. **Розширення модуля `catalog`**:
   - В `Product` додаються поля: `old_price: Money | None`,
     `images: tuple[ProductImage, ...]`, методи `update(...)`, `activate()`,
     `deactivate()`.
   - Use cases:
     - `ListTags` — повертає всі теги, відсортовані за групою та назвою.
     - `QuickCreateProduct` — створює товар з автогенерацією унікального `slug`
       (через `to_slug(name)` + перевірка в репозиторії) та прив'язкою фото через
       `MediaFacade`.
     - `UpdateProduct` — оновлює поля товару, теги та фото за `product_id`.
     - `ListAdminProducts` — повертає сторінку товарів (активні + неактивні) з
       пошуком `q` по назві/slug та фільтром `is_active`, `tag_slug`.
3. **Розширення модуля `orders`**:
   - `OrderStatus`: `new`, `confirmed`, `assembled`, `shipped`, `completed`,
     `cancelled`.
   - `OrderSource`: `storefront`, `instagram`, `telegram`, `phone`, `walk_in`.
   - Сутність `OrderStatusEntry(status, changed_at, comment)`.
   - Use cases:
     - `ListAdminOrders` — фільтрація за `status`, `delivery_date`,
       `delivery_method`, `order_source`, пошук `q` за номером, телефоном або
       ім'ям клієнта.
     - `GetAdminOrder` — отримання замовлення за `number` разом із позиціями та
       історією статусів.
     - `UpdateOrderAdmin` — зміна статусу (з записом у `orders_status_history`)
       та/або оновлення `internal_note`, `delivery_date`, `delivery_slot`.

## Модель даних (міграція 0003)
- Зміни в `catalog_products`:
  - `old_price_kopecks` (`int | null`, CHECK `old_price_kopecks IS NULL OR old_price_kopecks > price_kopecks`)
  - `updated_at` (`timestamptz`, default `now()`)
- Зміни в `orders_orders`:
  - `order_source` (`varchar(32)`, default `'storefront'`)
  - `utm_source` (`varchar(120) | null`)
  - `utm_medium` (`varchar(120) | null`)
  - `utm_campaign` (`varchar(160) | null`)
  - `landing_page` (`varchar(300) | null`)
  - `promo_code` (`varchar(64) | null`)
  - `discount_kopecks` (`int`, default `0`, CHECK `discount_kopecks >= 0`)
  - `internal_note` (`text`, default `''`)
  - `updated_at` (`timestamptz`, default `now()`)
- Нова таблиця `orders_status_history`:
  - `id` (`uuid`, PK)
  - `order_id` (`uuid`, FK → `orders_orders.id`, ON DELETE CASCADE)
  - `from_status` (`varchar(16) | null`)
  - `to_status` (`varchar(16)`)
  - `note` (`varchar(300)`, default `''`)
  - `changed_at` (`timestamptz`)

## Індекси (і для яких запитів)
| Індекс | Запит |
| --- | --- |
| `ix_orders_orders_status_created` на `orders_orders(status, created_at DESC)` | список замовлень в адмінці за статусом |
| `ix_orders_orders_delivery_date` на `orders_orders(delivery_date, created_at DESC)` | розклад салону на обрану дату доставки |
| `ix_orders_orders_created_at` на `orders_orders(created_at DESC)` | загальний список замовлень та аналітика за період |
| `ix_orders_orders_customer_phone` на `orders_orders(customer_phone, created_at DESC)` | пошук замовлень клієнта, розрахунок LTV та повторних покупок |
| `ix_orders_status_history_order_id` на `orders_status_history(order_id, changed_at)` | історія статусів замовлення (покриває FK `order_id`) |

## Запити та контроль N+1
- `ListAdminProducts`: `COUNT` + `SELECT catalog_products` + `selectinload(tags)` + `selectinload(media)` = **4 запити** константно.
- `ListAdminOrders`: `COUNT` + `SELECT orders_orders` + `selectinload(items)` + `selectinload(status_history)` = **4 запити** константно.
- `UpdateProduct`: 1 виклик `MediaFacade.get_assets` (якщо передано `media_ids`) + 1 вибірка тегів + оновлення продукту і пакетний перезапис тегів/фото.

## API
- `POST /api/v1/admin/auth/login` → `{token, expires_at}` (також встановлює HttpOnly cookie)
- `GET /api/v1/admin/auth/me` → `{role: "admin"}`
- `GET /api/v1/catalog/tags` → `list[TagOut]`
- `GET /api/v1/admin/catalog/products` → `AdminProductPageOut`
- `POST /api/v1/admin/catalog/products` → `201 AdminProductOut` (авто-slug)
- `PATCH /api/v1/admin/catalog/products/{product_id}` → `AdminProductOut`
- `GET /api/v1/admin/orders` → `AdminOrderPageOut`
- `POST /api/v1/admin/orders` → `201 AdminOrderOut`
- `GET /api/v1/admin/orders/{number}` → `AdminOrderOut`
- `PATCH /api/v1/admin/orders/{number}` → `AdminOrderOut`
