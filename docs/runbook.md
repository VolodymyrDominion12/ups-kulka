# Runbook: сервер «УПС! Кулька»

Як запустити магазин на VPS, викладати нові версії, відкочувати і
відновлювати з бекапу. Устрій описано в [`specs/012-deploy`](../specs/012-deploy/plan.md).

## 1. Що потрібно заздалегідь

- VPS: 2 vCPU, 4 ГБ RAM, 40+ ГБ диска, Ubuntu 24.04.
- Домен. У DNS — записи `A` на IP сервера для `example.ua`, `www.example.ua`
  і `staging.example.ua`.
- Доступ адміністратора до репозиторію на GitHub.

Далі `example.ua` — ваш домен, `SERVER` — IP сервера.

## 2. Підготовка сервера (один раз, від root)

```bash
apt update && apt install -y ca-certificates curl ufw
curl -fsSL https://get.docker.com | sh

adduser --disabled-password --gecos "" deploy
usermod -aG docker deploy
mkdir -p /opt/ups-kulka/env /srv/ups-kulka
chown -R deploy:deploy /opt/ups-kulka /srv/ups-kulka

ufw allow OpenSSH && ufw allow 80,443/tcp && ufw allow 443/udp && ufw enable
```

Ключ для деплою — на своєму комп'ютері:

```bash
ssh-keygen -t ed25519 -f ups-deploy -C github-deploy -N ""
ssh-copy-id -i ups-deploy.pub deploy@SERVER
ssh-keyscan SERVER        # це значення для SSH_KNOWN_HOSTS
```

## 3. Секрети на сервері

Скопіюйте приклади з репозиторію (`deploy/env/*.example`) у
`/opt/ups-kulka/env/` без `.example` і заповніть:

| Файл | Що заповнити |
| --- | --- |
| `edge.env` | `ACME_EMAIL`, `SITE_DOMAIN`, `STAGING_DOMAIN`; `EDGE_SITES="production staging"` |
| `production.env` | `SITE_URL`, `POSTGRES_PASSWORD`, `UPS_ADMIN_PASSWORD`, `UPS_ADMIN_SECRET_KEY`, Telegram, Monobank (порожній = онлайн-оплата вимкнена) |
| `staging.env` | те саме, але **інші** паролі; `SITE_NOINDEX=1` |

Паролі й ключі: `openssl rand -hex 24` (база), `openssl rand -hex 32` (ключ адмінки).
Права: `chmod 600 /opt/ups-kulka/env/*.env`.

API не стартує на сервері зі стандартним паролем адмінки `admin123` або з
ключем, коротшим за 32 символи, — це навмисно.

## 4. GitHub (один раз)

**Settings → Environments:** створіть `staging` і `production`.

- У кожному: секрети `SSH_HOST` (= SERVER), `SSH_USER` (= deploy),
  `SSH_PRIVATE_KEY` (вміст файлу `ups-deploy`), `SSH_KNOWN_HOSTS`;
  змінна `SITE_URL` (`https://staging.example.ua` / `https://example.ua`);
  за потреби — `SSH_PORT`.
- `production` → **Required reviewers**: ви. Тоді production чекає на кнопку
  «Approve», а staging викладається сам.

**Settings → Variables (Repository):** `STAGING_ENABLED` = `true`.
Без неї staging пропускається і йде одразу production.

**Пакети:** після першої збірки на сторінці репозиторію → Packages →
`ups-kulka-api` і `ups-kulka-web` → Package settings → Change visibility →
Public (репозиторій і так публічний). Тоді відкат вручну працює без входу в GHCR.

## 5. Перший запуск

1. Закомітьте `frontend/package-lock.json` (після `npm install`) і злийте в `main`.
2. Дочекайтеся зеленого CI → workflow **Deploy** збере образи і викладе staging.
3. Перевірте `https://staging.example.ua`, потім імпортуйте каталог:

```bash
ssh deploy@SERVER
cd /opt/ups-kulka
ENV=staging   # або production
app() { IMAGE_TAG=$(cat state/$ENV.tag) docker compose -p ups-kulka-$ENV \
  -f deploy/compose.prod.yml --env-file env/$ENV.env "$@"; }

app run --rm migrate python scripts/import_old_site.py   # товари й фото, кілька хвилин
app run --rm migrate python scripts/telegram_chat_id.py  # chat_id для сповіщень
```

Список `failed` у кінці імпорту — товари без фото (замалі чи недоступні);
їм фото додається вручну в адмінці `/admin`.

4. Усе гаразд → у GitHub → Actions → Deploy → **Approve** для production.
   Потім той самий імпорт для `ENV=production`.

## 6. Щоденна робота

| Задача | Команда (на сервері, з функцією `app` вище) |
| --- | --- |
| Що запущено | `app ps` |
| Логи | `app logs -f --tail 100 api web` |
| Перезапуск | `app restart api web` |
| Поточна версія | `cat state/production.tag` |
| Відкат на попередню | `deploy/deploy.sh production <тег>` (теги — у GitHub → Packages) |
| Змінили `env/*.env` | `deploy/deploy.sh production $(cat state/production.tag)` |
| Логи Caddy | `docker logs -f --tail 100 ups-kulka-edge-caddy-1` |

Якщо нова версія не піднялася, `deploy.sh` сам повертає попередню, а
workflow стає червоним. Міграції не відкочуються: вони лише додають
колонки й таблиці, тому стара версія коду працює з новою схемою.

## 7. Бекапи

Контейнер `backup` щодня робить дамп бази, щотижня — архів фото, у
`/srv/ups-kulka/<env>/backups`, і зберігає 14 днів.
Це той самий диск — **копіюйте папку кудись ще** (поки вручну:
`scp -r deploy@SERVER:/srv/ups-kulka/production/backups ./`).

Відновлення:

```bash
app stop web api
app exec -T db pg_restore --clean --if-exists -U ups -d ups_kulka \
  < /srv/ups-kulka/production/backups/db-<дата>.dump
tar -xzf /srv/ups-kulka/production/backups/media-<дата>.tar.gz -C /srv/ups-kulka/production
app start api web
```

## 8. Старий домен

Коли DNS `oops.kylka.shop` вказуватиме на SERVER: в `env/edge.env`
`EDGE_SITES="production staging old-domain"` і будь-який деплой (або
`deploy/deploy.sh production $(cat state/production.tag)`). Старий сайт
відповідатиме 301 на головну нового.
