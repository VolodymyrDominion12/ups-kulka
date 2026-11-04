# 015 — План реалізації

## Бекенд (модуль catalog)
- `domain/entities.py`: `RELATED_PRODUCTS_LIMIT = 8`.
- `ports.py`: `ProductRepository.list_related(slug, limit) -> list[Product]`.
- `repositories.py`: 2 запити — ids за спільними тегами (GROUP BY) + самі товари
  з `selectinload(tags, media)`; порядок зберігається за списком ids.
- `use_cases/list_related_products.py`: `ListRelatedProducts` → `list[ProductDTO]`.
- `presentation`: `GET /api/v1/catalog/products/{slug}/related` → `list[ProductOut]`.
- `container.py`: реєстрація use case.

## Фронтенд
- `shared/api/storefront.ts`: `catalogApi.listRelated(slug)` → `ProductOut[]`.
- `/tovar/[slug]/page.tsx`: блок «Схожі композиції» (сітка карток з «Додати»)
  + JSON-LD `BreadcrumbList`.

## Тести
- Unit: use case з фейком (виключення себе, порядок, ліміт).
- Integration: `list_related` + `assert_max_queries`; API-тест ендпоінта.
- Frontend: typecheck + build.

## Контракт
`make openapi` → оновити `contracts/openapi.json`.
