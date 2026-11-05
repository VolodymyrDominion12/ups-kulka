# 017 — Задачі

## Етап 1 — бекенд + базовий hero
- [x] Домен: `BannerCampaign`, валідація, `select_active`.
- [x] Міграція `0006_banner_campaigns` + індекс.
- [x] Репозиторій, UoW, контейнер.
- [x] `GetActiveBanner` + `GET /storefront/home-banner`.
- [x] Unit + integration + architecture + migration тести.
- [x] Фронт: `Hero` → `widgets/hero/HeroBalloons`, layout `image`.
- [x] `make openapi`, `make check`.

## Етап 2 — адмінка
- [x] Use cases create/update/publish/unpublish/duplicate/delete/list + admin API.
- [x] `BannersTab.tsx`: список, форма, завантаження фото, живе превʼю, дублювання.

## Етап 3 — макети
- [x] `split`, `collection`, промо-стрічка (`HeroSplit`, `HeroRibbon`, підбірка за `tag_slug`).

## Етап 4 — аналітика
- [x] Атрибуція кліку CTA та промо-стрічки (`utm_source=home_banner`, `utm_campaign=<campaign_id>`).

## Етап 5 — готові свята й ручний показ
- [x] `pinned` у домені (`activate_now`, `deactivate_now`), репозиторії та `GetActiveBanner`.
- [x] Міграція `0008_banner_campaigns_pinned` + частковий UNIQUE-індекс.
- [x] `SetBannerPinned` + `POST /admin/banners/{id}/activate|deactivate`.
- [x] Пресети 14 лютого, 8 березня, Різдво, Новий рік (`domain/presets.py`) +
      `GET /admin/banners/presets`.
- [x] Адмінка: блок «Готові святкові банери», «Створити й показати», «Показати зараз»,
      «Зупинити показ», бейдж ручного показу.
- [x] Unit + integration тести, `make openapi`, `make check`.
