# 017 — План реалізації

## Модуль
`ups_kulka.modules.banners` (domain / application / infrastructure / presentation / container).
Зображення лише через `MediaFacade` (без FK у `media_assets`).

## Модель даних (міграція `0006_banner_campaigns`, оборотна)
`banner_campaigns`: `id` uuid PK, `name`, `layout` (CHECK), `status` (draft/published),
`starts_at`, `ends_at` (CHECK ends>starts), `priority`, `headline`, `subtitle`,
`cta_label`, `cta_url`, `cta2_label`, `cta2_url`, `media_id`, `media_mobile_id`
(зображення підтягуються пакетно через `MediaFacade.get_assets`, без денормалізації), `image_alt`,
`theme`, `tag_slug`, `ribbon_text`, `ribbon_url`, `created_at`, `updated_at`.

## Індекси
| Індекс | Запит |
| --- | --- |
| `ix_banner_campaigns_active (status, starts_at, ends_at, priority DESC)` | активна кампанія на головній |

FK немає. Запит: `status='published' AND starts_at<=now AND ends_at>now ORDER BY priority DESC, starts_at DESC LIMIT 1`.

## Use cases
`GetActiveBanner`, `ListBanners`, `CreateBanner`, `UpdateBanner`, `PublishBanner`,
`DuplicateBanner`, `DeleteBanner`. Вибір активної — чиста доменна функція (час інжектується).

## API
- `GET /api/v1/storefront/home-banner` (публічний, `Cache-Control: s-maxage=60, stale-while-revalidate`).
- `/api/v1/admin/banners` (GET, POST), `/{id}` (GET, PATCH, DELETE), `/{id}/publish`, `/{id}/duplicate`.
- Після змін — `make openapi`.

## Фронтенд
`widgets/hero/` (`HeroBalloons`, `HeroImage`, `HeroSplit`, `HeroRibbon`), `app/page.tsx`
додає `bannerApi.getActive()` в `Promise.all`; адмінка `features/admin/BannersTab.tsx`
(список зі статусами, форма, превʼю, дублювання); подія аналітики кліку CTA.

## Тести
- Unit: вибір активної (перетин, пріоритет, межі, TZ, fallback), валідація за layout, дублювання.
- Integration (PostgreSQL): репозиторій, API, `query_counter` ≤ 2, `EXPLAIN` індексу.
- Architecture: доступ до media лише через `MediaFacade`.
- Migrations: з нуля, `alembic check`.
