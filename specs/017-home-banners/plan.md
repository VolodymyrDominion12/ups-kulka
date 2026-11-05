# 017 — План реалізації

## Модуль
`ups_kulka.modules.banners` (domain / application / infrastructure / presentation / container).
Зображення лише через `MediaFacade` (без FK у `media_assets`).

## Модель даних (міграції `0006_banner_campaigns`, `0008_banner_campaigns_pinned`, оборотні)
`banner_campaigns`: `id` uuid PK, `name`, `layout` (CHECK), `status` (draft/published),
`pinned` (bool, ручний показ поза розписом), `starts_at`, `ends_at` (CHECK ends>starts),
`priority`, `headline`, `subtitle`, `cta_label`, `cta_url`, `cta2_label`, `cta2_url`,
`media_id`, `media_mobile_id` (зображення підтягуються пакетно через
`MediaFacade.get_assets`, без денормалізації), `image_alt`, `theme`, `tag_slug`,
`ribbon_text`, `ribbon_url`, `created_at`, `updated_at`.

`0008` додає `pinned boolean NOT NULL DEFAULT false` (default прибирається після
заповнення) і частковий UNIQUE-індекс, тож ручний показ має щонайбільше одна кампанія.

## Індекси
| Індекс | Запит |
| --- | --- |
| `ix_banners_campaigns_active (status, starts_at, ends_at)` | активна кампанія на головній |
| `ix_banners_campaigns_starts_at (starts_at)` | список кампаній в адмінці (`ORDER BY starts_at DESC`) |
| `uq_banners_campaigns_pinned (pinned) WHERE pinned` | ручний показ: унікальність + пошук `pinned` |

FK немає. Запит: `status='published' AND (pinned OR (starts_at<=now AND ends_at>now)) ORDER BY pinned DESC, priority DESC, starts_at DESC LIMIT 1` — один SQL.

## Use cases
`GetActiveBanner`, `ListBanners`, `CreateBanner`, `UpdateBanner`, `SetBannerPublished`,
`SetBannerPinned` (activate/deactivate), `ListBannerPresets`, `DuplicateBanner`, `DeleteBanner`.
Вибір активної — доменний `is_active_at` (час інжектується); ручний показ — `activate_now()`.
`SetBannerPinned(pinned=True)` публікує кампанію, знімає `pinned` з інших і комітить разом.

Святкові пресети — `domain/presets.py` (`HolidayPreset`, `HOLIDAY_PRESETS`):
14 лютого, 8 березня, Різдво (25 грудня), Новий рік. `period(now)` повертає поточне
або найближче вікно у `Europe/Kyiv`; назва кампанії — за роком свята.

## API
- `GET /api/v1/storefront/home-banner` (публічний, `Cache-Control: no-store`): ручне
  перемикання в адмінці діє з наступного запиту; головна теж читає без кешу.
- `/api/v1/admin/banners` (GET, POST), `/{id}` (GET, PATCH, DELETE), `/{id}/publish`,
  `/{id}/unpublish`, `/{id}/activate`, `/{id}/deactivate`, `/{id}/duplicate`.
- `GET /api/v1/admin/banners/presets` — чотири готові свята з датами найближчого сезону.
- Після змін — `make openapi`.

## Фронтенд
`widgets/hero/` (`HeroBalloons`, `HeroImage`, `HeroSplit`, `HeroRibbon`), `app/page.tsx`
додає `bannerApi.getActive()` в `Promise.all`; адмінка `features/admin/BannersTab.tsx`
(список зі статусами, форма, превʼю, дублювання, блок «Готові святкові банери»,
кнопки «Показати зараз» / «Зупинити показ»); подія аналітики кліку CTA.
`presetToPayload()` у `shared/lib/banner.ts` перетворює пресет у тіло `POST /admin/banners`.

## Тести
- Unit: вибір активної (перетин, пріоритет, межі, TZ, fallback, `pinned`), валідація за
  layout, активація/деактивація, зняття з публікації, пресети (дати в Києві, рік у назві).
- Integration (PostgreSQL): репозиторій, API, `pinned` поза датами, унікальність ручного
  показу, `query_counter` ≤ 2, `EXPLAIN` індексу.
- Architecture: доступ до media лише через `MediaFacade`.
- Migrations: з нуля, `alembic check`.
