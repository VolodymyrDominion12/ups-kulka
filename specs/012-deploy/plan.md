# 012 — План

## Сервер
Один VPS (2 vCPU, 4 ГБ), Ubuntu 24.04, Docker з compose. Каталог `/opt/ups-kulka`:
`deploy/` (копіюється з репозиторію під час кожного деплою), `env/*.env`
(секрети, лише на сервері), `state/<env>.tag` (поточна версія).
Дані: `/srv/ups-kulka/<env>/{media,backups}`.

## Контейнери
| Стек | Сервіси | Файл |
| --- | --- | --- |
| `ups-kulka-edge` | caddy (80/443, HTTP/3) | `deploy/edge/compose.yml` |
| `ups-kulka-production`, `ups-kulka-staging` | web, api, db (postgres 17), backup, migrate (разово) | `deploy/compose.prod.yml` |

Caddy бачить `web` і `api` через спільну мережу `edge` під іменами
`<env>-web`, `<env>-api`. Сайти Caddy вмикає `EDGE_SITES` у `env/edge.env`
(`production`, `staging`, `old-domain`).

Маршрути: `/media/*` → файли з диска (immutable, рік), `/api/*` → API,
решта → Next.js. `www.` → 301 на основний домен.

## Образи
- API: `backend/Dockerfile`, тепер із `scripts/` і `seed/` (імпорт каталогу на
  сервері), uvicorn довіряє `X-Forwarded-*` (API доступний лише через Caddy).
- Вітрина: `frontend/Dockerfile`, Next.js `output: "standalone"`, користувач
  10001, healthcheck на `/robots.txt` (без запитів до API).
- Теги: короткий SHA коміту і `main`. Реєстр: GHCR.

## Конфігурація під час запуску
- `SITE_URL` (замість вбудованого при збірці `NEXT_PUBLIC_SITE_URL`) —
  canonical, sitemap, schema.org; `robots.txt` динамічний.
- `SITE_NOINDEX=1` на staging закриває сайт у `robots.txt`.
- `Settings` відмовляється стартувати на `production`/`staging` зі
  стандартним `UPS_ADMIN_PASSWORD` або `UPS_ADMIN_SECRET_KEY` коротшим за 32 символи.

## Деплой (`deploy/deploy.sh <env> <tag>`)
1. Каталоги даних (власник media — uid 10001) через `docker run`, без sudo.
2. Мережа `edge`, Caddy up, `caddy reload`.
3. `pull` → `db` up → `migrate` (`alembic upgrade head`) → `up --wait`.
4. Помилка → логи і повернення на тег зі `state/<env>.tag`. Міграції лише
   додають (AGENTS.md, розділ 5), тому стара версія працює на новій схемі.

## CI/CD
- `ci.yml`: додано job `frontend` (тести, типи, `next build`).
- `deploy.yml`: після зеленого CI на `main` (або вручну) → `images` →
  `staging` (якщо `STAGING_ENABLED=true`) → `production` (GitHub Environment
  з required reviewers) → smoke-тест (`deploy/ci/smoke.sh`).
- На сервер — по SSH з ключем лише для деплою; `docker login` до GHCR
  тимчасовим `GITHUB_TOKEN`, після деплою — `logout`.

## Відхилення від технічного плану
Redis і фоновий worker поки не розгортаємо: бекенд їх не використовує
(фото обробляються під час завантаження, сповіщення — одразу). Додамо разом
із першою функцією, якій потрібна черга. Бекапи поки локальні; винесення на
S3-сумісне сховище — окрема задача.
