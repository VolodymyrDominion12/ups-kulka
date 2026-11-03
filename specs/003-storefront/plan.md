# 003 — План

## Маршрути (`frontend/src/app`)
| URL | Файл | Рендер |
| --- | --- | --- |
| `/` | `page.tsx` (сам обгортає себе в `ShopShell`) | сервер, дані кешуються 5 хв |
| `/kulky`, `/kulky/[tag]` | `(shop)/kulky/...` | сервер, `?page=N` |
| `/tovar/[slug]` | `(shop)/tovar/[slug]/page.tsx` | сервер, 404 через `notFound()` |
| `/koshyk`, `/oformlennia`, `/diakuiemo` | `(shop)/...` | клієнт, `noindex` |
| `/sitemap.xml`, `/robots.txt` | `sitemap.ts`, `robots.ts` | сервер |
| `/admin` | без змін; власний `admin/layout.tsx` з метаданими і manifest адмінки |

Решта сторінок вітрини — у групі `(shop)`, її `layout.tsx` теж рендерить
`widgets/ShopShell` (кошик, шапка, підвал, нижня панель, мітки UTM).
Помилки сторінок (API недоступний) ловить `app/error.tsx`.

Сторінки вітрини — `dynamic = "force-dynamic"`, а запити до API кешуються
через `fetch(..., { next: { revalidate: 300 } })`. Так `next build` не
залежить від запущеного API, а покупці все одно отримують кешовані дані.

## Шари (Feature-Sliced Design)
- `shared/api/storefront.ts` — читання каталогу на сервері
  (`API_INTERNAL_URL` → `NEXT_PUBLIC_API_URL` → `http://localhost:8000`) і
  відправка замовлення з браузера через rewrite `/api`.
- `shared/lib/` — чиста логіка без React: гроші, телефон, UTM, кошик
  (reducer), побудова тіла замовлення, підписи. Покрита тестами Vitest.
- `shared/config/shop.ts` — телефон, Instagram, URL сайту.
- `entities/product/` — `ProductImage` (`srcset` з варіантів 320–1280w WebP,
  розмитий плейсхолдер, заглушка без фото), `ProductCard`, `Price`.
- `features/cart/` — провайдер кошика, кнопка «Додати», кнопка кошика в шапці,
  нижня панель на телефоні.
- `features/checkout/` — форма оформлення.
- `features/marketing/UtmCapture` — запам'ятовує мітки першого входу.
- `widgets/` — шапка, перший екран, чипи категорій, сітка з пагінацією,
  переваги, FAQ, підвал.

## API (без змін бекенду)
`GET /api/v1/catalog/products?tag&limit&offset`, `GET /api/v1/catalog/products/{slug}`,
`GET /api/v1/catalog/tags`, `GET /api/v1/orders/checkout-options`, `POST /api/v1/orders`.

## Зображення
Варіанти вже готові (009): `<img srcset>` без `next/image`, тож сервер не
перестискає фото на кожен запит. Розміри задані, `aspect-ratio: 1`, без CLS.
