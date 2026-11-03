# Архітектура бекенду

Модульний моноліт за чистою архітектурою (ports & adapters). Повний технічний
план: https://claude.ai/artifact/AWmxtaAovWYGUxaVfGZJ93

## Напрям залежностей

```text
            ┌──────────────────────┐
HTTP  ───▶  │ presentation (router)│ ──┐
            └──────────────────────┘   │ викликає use case (через DI)
                                       ▼
            ┌──────────────────────┐
            │ application          │  use cases, порти (Protocol), DTO
            └──────────────────────┘
                       │ використовує
                       ▼
            ┌──────────────────────┐
            │ domain               │  сутності, value objects, правила
            └──────────────────────┘
                       ▲
            ┌──────────────────────┐
            │ infrastructure       │  реалізує порти: SQLAlchemy, платежі,
            └──────────────────────┘  Telegram, файли
```

`container.py` (composition root) — єдине місце, яке знає про всі шари й
з'єднує порти з реалізаціями.

## Потік запиту

1. FastAPI викликає функцію роутера; Pydantic валідує вхід.
2. `dependency-injector` підставляє use case, зібраний із фабрикою UoW.
3. Use case відкриває UoW (сесія + транзакція), працює з репозиторіями й
   доменом, комітить.
4. Use case повертає DTO; роутер перетворює його у схему відповіді.
5. Доменні помилки (`DomainError`) перетворюються в HTTP-відповіді глобальним
   обробником (`shared/presentation/errors.py`).

## Рішення (ADR)

- [0001 — Чиста архітектура і модульний моноліт](adr/0001-clean-architecture.md)
- [0002 — dependency-injector для DI](adr/0002-dependency-injector.md)
- [0003 — Контроль N+1 та індексів](adr/0003-n-plus-one-and-indexes.md)
