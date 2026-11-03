# 011 — Задачі (Аналітика продажів, Маркетинг та CRM)

- [x] Доменні правила та DTO аналітики: метрики виручки, порівняння періодів (дельта у `%`), RFM/LTV-сегментація клієнтів, обчислення вікна річниць замовлень + unit-тести
- [x] Порти та use cases `GetAnalyticsDashboard`, `ListCustomersCrm`, `GetOrderAnniversaries` + unit-тести з фейками
- [x] Фасад `CatalogFacade.products_for_analytics` для розрізу продажів за вимірами тегів (`TagGroup`) та пошуку товарів без продажів
- [x] SQLAlchemy-реалізація аналітичних запитів без N+1 + інтеграційні тести з `assert_max_queries`
- [x] Роутер `/api/v1/admin/analytics/*`, Pydantic-схеми, оновлення `contracts/openapi.json`
- [ ] Інтерактивні дашборди в мобільній адмін-панелі Next.js (`/admin/analytics`, `/admin/customers`)
