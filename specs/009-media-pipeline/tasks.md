# 009 — Задачі (Конвеєр зображень та фото товарів)

- [x] Домен `media`: `MediaAsset`, `ImageDimensions`, помилки (`InvalidMediaFile`, `MediaFileTooLarge`, `ImageTooSmall`) + unit-тести
- [x] Порти `ImageProcessor`, `MediaStorage`, `MediaRepository`, `MediaUnitOfWork` та use cases `UploadMedia`, `ListMediaAssets` + unit-тести з фейками
- [x] Інфраструктура `media`: `PillowImageProcessor` (EXIF transpose, очищення метаданих, кроп 4:5, генерація WebP та `blur_data_url`), `LocalFileMediaStorage`, `SqlAlchemyMediaRepository`
- [x] Розширення домену та use cases `catalog`: підтримка `images: tuple[ProductImage, ...]` у `Product`, прив'язка `media_ids` через `MediaFacade`
- [x] Таблиці `media_assets` та `catalog_product_media`, міграція Alembic, перевірка індексів
- [x] Презентаційний шар `media` (`POST /api/v1/admin/media`, `GET /api/v1/admin/media`), інтеграційні тести та перевірка відсутності N+1 (`assert_max_queries`)
- [x] Оновити `contracts/openapi.json` (`make openapi`) та пройти `make check`
