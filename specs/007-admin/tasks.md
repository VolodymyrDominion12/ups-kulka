# 007 — Задачі (Мобільна адмін-панель)

- [x] Модуль `admin_auth`: домен, use cases (`LoginAdmin`, `VerifyAdminSession`), інфраструктура підпису токенів (HMAC-SHA256), роутер `/api/v1/admin/auth` + unit-тести
- [x] Розширення домену `catalog`: `old_price`, `images`, автогенерація унікального `slug`, редагування та активація/деактивація товару + unit-тести
- [x] Нові use cases `catalog`: `ListTags`, `QuickCreateProduct`, `UpdateProduct`, `ListAdminProducts` + unit-тести з фейками
- [x] Розширення домену `orders`: статуси `OrderStatus`, джерела `OrderSource`, маркетингові поля, історія статусів `OrderStatusEntry`, методи переходу статусів + unit-тести
- [x] Нові use cases `orders`: `ListAdminOrders`, `GetAdminOrder`, `UpdateAdminOrder`, `CreateAdminOrder` + unit-тести з фейками
- [x] ORM-моделі, міграція, індекси, репозиторії та інтеграційні тести (з перевіркою `assert_max_queries`)
- [x] Роутери адмінки для каталогу й замовлень, оновлення `contracts/openapi.json`
- [ ] Мобільна PWA адмін-панель у `frontend/` (`/admin/*`)
