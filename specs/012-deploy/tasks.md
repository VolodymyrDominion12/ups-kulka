# 012 — Задачі

- [x] Dockerfile вітрини (standalone, не-root, healthcheck), `.dockerignore`
- [x] Образ API зі скриптами імпорту; довіра до `X-Forwarded-*`
- [x] `SITE_URL` під час запуску, динамічний `robots.txt`, `SITE_NOINDEX` + тести
- [x] API не стартує на сервері зі стандартними секретами адмінки + тести
- [x] `deploy/compose.prod.yml`, `deploy/edge/` (Caddy), `backup.sh`, приклади env
- [x] `deploy/deploy.sh` з міграціями, очікуванням healthcheck і відкатом
- [x] CI: job `frontend`; `deploy.yml` (GHCR → staging → production → smoke)
- [x] `docs/runbook.md`
- [ ] Закомітити `frontend/package-lock.json` (потім CI і Docker перейдуть на `npm ci`)
- [ ] Обрати домен і VPS, налаштувати сервер і GitHub за runbook
- [ ] Перший деплой на staging, імпорт каталогу, перевірка; потім production
- [ ] Бекапи поза сервером (restic/rclone на S3-сумісне сховище)
- [ ] Редирект старого домену після перенесення DNS (`EDGE_SITES` += `old-domain`)
