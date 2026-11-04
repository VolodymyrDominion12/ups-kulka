# 002 — План реалізації

## Модель даних (міграція `0004_tag_seo`)
Додаємо до `catalog_tags`:
- `seo_title` VARCHAR(160) NOT NULL DEFAULT ''
- `seo_description` VARCHAR(300) NOT NULL DEFAULT ''
- `intro_text` TEXT NOT NULL DEFAULT ''
- `seo_text` TEXT NOT NULL DEFAULT ''
- `faq` JSONB NOT NULL DEFAULT '[]'  — список `{"question": str, "answer": str}`

Нових індексів не треба: тегів десятки, а join за `tag_id` уже покритий
`ix_catalog_product_tags_tag_id` і PK `catalog_product_tags(product_id, tag_id)`.

## Бекенд (модуль catalog)
- `domain/entities.py`: `FaqItem` (frozen), поле `faq` та SEO-поля у `Tag`,
  метод `update_seo`, `has_unique_text`, `is_indexable(product_count)`,
  константа `MIN_PRODUCTS_FOR_INDEXING = 6`, валідація довжин.
- `application/dto.py`: `FaqItemDTO`, `TagSummaryDTO` (id, group, slug, name,
  product_count, is_indexable), `TagDetailDTO` (summary + seo + faq),
  `UpdateTagSeoCommand`.
- `application/ports.py`: `TagRepository.get_by_slug_with_count`,
  `get_by_id_with_count`, `list_with_counts`, `save`.
- Use cases: `GetTagDetail` (public), `ListTags` → повертає `TagSummaryDTO`,
  `UpdateTagSeo` (admin, авторизація через `CatalogAdminGuard`).
- `infrastructure/repositories.py`: один GROUP BY запит для лічильників активних
  товарів по тегах.
- `presentation`: `TagSummaryOut`, `TagDetailOut`, `FaqItemOut`, `UpdateTagSeoIn`;
  роутери `GET /catalog/tags/{slug}`, `PATCH /admin/catalog/tags/{id}`.

## Фронтенд
- `shared/api/storefront.ts`: тип `TagSummaryOut` (розширює `TagOut` полями
  `product_count`, `is_indexable`), `TagDetailOut`, `FaqItemOut`; `catalogApi.getTag`.
- `shared/api/admin.ts`: `adminApi.updateTagSeo`, `getTagSeo`.
- `/kulky/[tag]/page.tsx`: H1=seo_title, вступ, SEO-текст, FAQ, JSON-LD
  (`FAQPage`, `BreadcrumbList`), `noindex` для неіндексованих.
- `CatalogPage.tsx`: рендер intro/seo_text/FAQ.
- `sitemap.ts`: фільтр `is_indexable`.
- Адмінка: нова вкладка «Теги» з редактором SEO-полів і FAQ.

## Тести
- Unit: домен `Tag.update_seo`/`is_indexable`, use cases з фейками.
- Integration: репозиторій (лічильники одним запитом, `assert_max_queries`), API.
- Frontend: unit-тест хелперів (якщо є чиста логіка), typecheck + build.

## Контракт
`make openapi` → оновити `contracts/openapi.json` (нові ендпоінти/схеми).
