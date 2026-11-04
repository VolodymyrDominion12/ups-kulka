# 016 — План реалізації

Фронтенд лише (без змін API/БД).

## Файли
- `app/(shop)/dostavka/page.tsx` — доставка і оплата (+ FAQ).
- `app/(shop)/kontakty/page.tsx` — контакти + Instagram CTA.
- `app/(shop)/pro-nas/page.tsx` — про нас.
- `widgets/LocalBusiness.tsx` (або інлайн у `app/layout.tsx`) — JSON-LD `LocalBusiness`.
- `app/layout.tsx` — підключити `LocalBusiness`.
- `widgets/SiteHeader.tsx`, `widgets/SiteFooter.tsx` — посилання на сторінки.
- `app/sitemap.ts` — додати три URL.

## Контент
Беремо з `SHOP` (телефон, Instagram, місто) + маркетингові тексти в коді сторінок.

## Тести
- `npm run typecheck`, `npm test`, `npm run build`.
- Сторінки статичні (без логіки), тому окремі unit-тести не потрібні.
