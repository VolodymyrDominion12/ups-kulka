# 002 — Задачі

- [ ] Міграція `0004_tag_seo` (оборотна).
- [ ] Домен: `FaqItem`, SEO-поля `Tag`, `update_seo`, `is_indexable`, валідація + unit-тести.
- [ ] DTO: `FaqItemDTO`, `TagSummaryDTO`, `TagDetailDTO`, `UpdateTagSeoCommand`.
- [ ] Порти + репозиторій (GROUP BY лічильники) + mappers + tables.
- [ ] Use cases: `GetTagDetail`, `UpdateTagSeo`, оновлений `ListTags` + unit-тести.
- [ ] Схеми + роутери + DI-реєстрація + API-тести.
- [ ] Інтеграційні тести репозиторію (`assert_max_queries`).
- [ ] `make openapi` → оновити `contracts/openapi.json`.
- [ ] Фронтенд: типи/API, сторінка `/kulky/[tag]`, `CatalogPage`, `sitemap`.
- [ ] Адмінка: вкладка «Теги» (SEO + FAQ).
- [ ] `make check` (бекенд) і `typecheck + test + build` (фронтенд) зелені.
