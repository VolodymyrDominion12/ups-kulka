# УПС! Кулька — інтернет-магазин

Монорепо: FastAPI-бекенд (чиста архітектура), Next.js-фронтенд (буде додано),
Docker-деплой на VPS.

**Перед роботою прочитай [AGENTS.md](AGENTS.md)** — правила для людей і AI-агентів.

## Швидкий старт (бекенд)

Потрібно: Python 3.13, [uv](https://docs.astral.sh/uv/), Docker.

```bash
cd backend
cp .env.example .env
make install      # uv sync
make up           # PostgreSQL + Redis у Docker
make migrate      # міграції
make run          # http://localhost:8000/docs
make check        # усе, що перевіряє CI

# каталог зі старого сайту (211 товарів, specs/010-import-old-site)
uv run python scripts/import_old_site.py
```

Онлайн-оплата (monobank) і сповіщення в Telegram вмикаються змінними в
`backend/.env` — див. `.env.example`, specs/006 і specs/008.

Інтеграційні тести самі піднімають PostgreSQL через testcontainers (потрібен
запущений Docker) або використовують `TEST_DATABASE_URL`.

## Вітрина й адмінка (фронтенд)

Потрібно: Node.js 22. Бекенд має працювати на `http://localhost:8000`.

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev        # http://localhost:3000 — вітрина, /admin — адмінка
npm test           # Vitest: кошик, оформлення, телефон, UTM
npm run typecheck
npm run build
```

## Документи

- [AGENTS.md](AGENTS.md), [backend/AGENTS.md](backend/AGENTS.md) — правила
- [docs/architecture.md](docs/architecture.md), [docs/adr/](docs/adr/) — архітектура
- [.specify/memory/constitution.md](.specify/memory/constitution.md) — принципи
- [specs/](specs/) — специфікації функцій
- [docs/design/](docs/design/) — дизайн вітрини: токени, демо `preview.html`
