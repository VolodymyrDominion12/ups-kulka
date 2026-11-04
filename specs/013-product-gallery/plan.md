# 013 — План реалізації

## Обсяг
Фронтенд лише. Без змін БД, міграцій, API-контракту.

## Модель даних
Без змін. Використовуємо наявні `ProductImageOut` (`media_id`, `position`,
`variants`, `blur_data_url`) і `adminApi.uploadMedia` / `updateProduct` /
`quickCreateProduct`.

## Компоненти та файли

| Файл | Що |
| --- | --- |
| `src/shared/lib/gallery.ts` (новий) | Чисті функції: `cycleIndex`, `reorderMediaIds`, `moveMediaToFront`, `removeMediaId`, `largestImageSrc`. |
| `src/shared/lib/__tests__/gallery.test.ts` (новий) | Unit-тести цих функцій. |
| `src/entities/product/ProductGallery.tsx` (новий) | Клієнтський компонент: головне фото, мініатюри, lightbox. |
| `src/app/(shop)/tovar/[slug]/page.tsx` | Використати `ProductGallery` замість статичного блоку фото. |
| `src/features/admin/CatalogManageTab.tsx` | Блок «Фото» в режимі редагування: додати/видалити/зробити головним/переставити. |
| `src/features/admin/QuickPublishTab.tsx` | Ліміт 6 → 10 фото, текст «До 10 фото». |

## Технічні рішення
- Lightbox — на Tailwind + `lucide-react`, без нових залежностей. Портал не
  потрібен: рендеримо `fixed inset-0 z-50` усередині компонента.
- Доступність: lightbox — `role="dialog" aria-modal="true"`, кнопки мають
  `aria-label`, фокус повертається на кнопку відкриття після закриття.
- Клавіатура: `Escape`, `ArrowLeft`, `ArrowRight` (лише коли lightbox відкритий).
- Свайп: прості обробники `touchstart`/`touchend` з порогом ~40px.
- Головне фото — `fetchPriority="high"` + `eager`; решта — `lazy` (не деградує LCP).
- Lightbox показує найбільший варіант: `1280w` → `original` → `960w`.

## Тести
`npm run typecheck`, `npm test` (unit-тести `gallery.ts`), `npm run build`.
Інтеграційні тести бекенду не зачіпаються (змін API немає).

## Індекси / запити
Немає (без змін БД).
