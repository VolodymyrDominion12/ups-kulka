# 014 — План реалізації

## Модель даних (міграція `0005_product_search`)
- `CREATE EXTENSION IF NOT EXISTS pg_trgm`.
- GIN-індекси: `ix_catalog_products_name_trgm` (на `name`),
  `ix_catalog_products_description_trgm` (на `description`) — прискорюють
  `ILIKE '%q%'`.

## Бекенд (модуль catalog)
- `domain/entities.py`: `ProductSort(StrEnum)` — `newest`, `price_asc`, `price_desc`.
- `application/dto.py`: `ListProductsQuery` + `q: str | None`, `sort: str`,
  `on_sale: bool | None`.
- `ports.py`: `list_active(..., q, sort, on_sale)`.
- `repositories.py`: `_paginate` приймає `order_by`; пошук через `ILIKE %q%`
  по name/description/slug; `on_sale` → `old_price_kopecks IS NOT NULL`.
- `presentation`: query-параметри `q`, `sort` (Literal), `on_sale`.

## Фронтенд
- `shared/api/storefront.ts`: `listProducts` + `q`, `sort`, `on_sale`.
- `widgets/CatalogControls.tsx` (клієнтський): пошук (форма GET), сортування,
  перемикач «Акції» — оновлює URL через `useRouter`/`useSearchParams`.
- `/kulky` і `/kulky/[tag]`: читають `q`/`sort`/`sale` з searchParams, передають
  у `CatalogPage`; `noindex` + canonical без параметрів, коли є фільтри.
- `CatalogPage`: приймає `q`/`sort`/`sale`, передає в `listProducts`, рендерить
  `CatalogControls`.

## Тести
- Unit: `ProductSort`, пагінація/сортування.
- Integration: пошук, сортування, on_sale, `assert_max_queries`.
- API: параметри, 422 на невалідний sort.
- Frontend: typecheck + build.

## Контракт
`make openapi` → оновити `contracts/openapi.json`.
