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
