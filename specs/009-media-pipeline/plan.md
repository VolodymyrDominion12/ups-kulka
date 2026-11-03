# 009 — План (Конвеєр зображень та фото товарів)

## Модулі й межі
- Новий модуль `ups_kulka.modules.media` за чистою архітектурою (`domain`,
  `application`, `infrastructure`, `presentation`, `container`).
- Публічний фасад `ups_kulka.modules.media.application.public.MediaFacade`
  надає пакетний метод `get_assets(ids: Sequence[UUID]) -> dict[UUID, MediaAssetDTO]`,
  щоб модуль `catalog` перевіряв існування `media_ids` і отримував дані фото
  лише через публічний фасад, не торкаючись таблиць `media` напряму
  (правило з `AGENTS.md`, розділ 3).
- У `catalog` зберігається таблиця зв'язку `catalog_product_media` з денормалізованими
  полями для швидкого читання на вітрині (`media_id`, `position`, `url_prefix`,
  `blur_data_url`, `width`, `height`), щоб список товарів у каталозі не робив
  міжмодульних JOIN-ів у чужу таблицю і вкладався в `selectinload`.

## Модель даних (міграція 0003)
- `media_assets`:
  - `id` (uuid, PK)
  - `original_filename` (varchar(255))
  - `mime_type` (varchar(64))
  - `file_size_bytes` (int, CHECK > 0)
  - `width` (int, CHECK > 0)
  - `height` (int, CHECK > 0)
  - `url_prefix` (varchar(255)) — наприклад `/media/<uuid>`
  - `variants_json` (text / json) — наявні варіанти (`320w`, `640w`, `960w`, `1280w`, `original`)
  - `blur_data_url` (text) — компактний data URL `image/webp;base64,...` (16×20 px)
  - `created_at` (timestamptz)
- `catalog_product_media`:
  - `product_id` (uuid, FK → `catalog_products.id`, ON DELETE CASCADE)
  - `media_id` (uuid) — без FK у чужий модуль `media_assets`
  - `position` (int, CHECK >= 0)
  - `url_prefix` (varchar(255))
  - `blur_data_url` (text)
  - `width` (int)
  - `height` (int)
  - PK: `(product_id, position)`

## Індекси (і для яких запитів)
| Індекс | Запит |
| --- | --- |
| PK `media_assets(id)` | пошук медіа за `id` та пакетна вибірка `WHERE id IN (...)` |
| `ix_media_assets_created_at` на `media_assets(created_at DESC)` | галерея останніх завантажених фото в адмінці |
| PK `catalog_product_media(product_id, position)` | впорядковані фото товару (`selectinload`, покриває FK `product_id`) |
| `ix_catalog_product_media_media_id` на `catalog_product_media(media_id)` | пошук товарів, де використовується конкретне фото |

## Обробка зображень (`infrastructure`)
- Порт `ImageProcessor` у `media/application/ports.py`.
- Реалізація `PillowImageProcessor` (Pillow з підтримкою WebP/AVIF + `ImageOps.exif_transpose`):
  1. Відкриває зображення з байтів, перевіряє цілісність і мінімальний розмір (200×200).
  2. Повертає за EXIF (`ImageOps.exif_transpose`), переводить у колірний простір `RGB` (sRGB), відкидає усі EXIF/GPS-метадані.
  3. Кадрує за центром у пропорцію `4:5` (`width : height = 4 : 5`).
  4. Генерує варіанти шириною `320`, `640`, `960`, `1280` px (без апскейлу, якщо оригінал менший, але завжди створює стандартні ключі) у форматі `.webp` (quality=82) та `.avif` (якщо плагін доступний, quality=65).
  5. Генерує `blur_data_url` (розмір 16×20 px у WebP base64, ~150–250 байт).
- Порт `MediaStorage` зберігає файли в `settings.media_root` (за замовчуванням `./var/media` локально). FastAPI роздає `/media` через `StaticFiles` у dev-режимі, а на проді їх віддає напряму Caddy з `Cache-Control: public, max-age=31536000, immutable`.

## Запити та контроль N+1
- Завантаження фото `UploadMedia`: 1 `INSERT` у `media_assets`.
- Отримання списку товарів `ListProducts`: `COUNT` + `SELECT catalog_products` + `selectinload(tags)` + `selectinload(media)` = **4 запити** константно (перевіряється `assert_max_queries(4)` на 1 та 12+ товарах).

## API
- `POST /api/v1/admin/media` (multipart/form-data `file`) → `201 MediaAssetOut`
- `GET /api/v1/admin/media?limit=24&offset=0` → `MediaAssetPageOut` (останні завантажені фото з телефона)
