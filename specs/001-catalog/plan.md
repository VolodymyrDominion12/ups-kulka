# 001 — План

## Модель даних
- `catalog_products`: id (uuid, PK), slug (UNIQUE), name, description,
  price_kop (int, CHECK > 0), is_active (bool), created_at (timestamptz).
- `catalog_tags`: id (uuid, PK), group (text: occasion | recipient | color |
  theme | type | age), slug (UNIQUE — slug глобально унікальний, щоб товар
  посилався на тег лише за slug), name.
- `catalog_product_tags`: product_id (FK), tag_id (FK), PK (product_id, tag_id).

## Індекси (і для яких запитів)
| Індекс | Запит |
| --- | --- |
| `UNIQUE catalog_products(slug)` | товар за slug |
| `catalog_products(is_active, created_at, id)` | список активних, новіші першими |
| `UNIQUE catalog_tags(slug)` | пошук тегу, фільтр списку за slug тегу |
| PK `catalog_product_tags(product_id, tag_id)` | теги товару (FK product_id) |
| `catalog_product_tags(tag_id)` | товари за тегом (FK tag_id) |

## Запити
- Список: count + сторінка товарів (з `EXISTS` по тегу) + `selectinload`
  тегів = **3 запити** незалежно від кількості товарів і тегів
  (`tests/integration/test_catalog_queries.py`).
- Товар за slug: 1 + 1 (теги) = 2 запити.

## API
- `POST /api/v1/catalog/tags` → 201 TagOut
- `POST /api/v1/catalog/products` → 201 ProductOut
- `GET /api/v1/catalog/products/{slug}` → ProductOut
- `GET /api/v1/catalog/products?tag=&limit=&offset=` → ProductPage
