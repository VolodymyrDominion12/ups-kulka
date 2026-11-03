# ADR 0002 — dependency-injector для DI

Статус: прийнято, 2026-11-03

## Контекст
Use cases залежать від портів (репозиторії, UoW, шлюзи). Потрібно одне місце,
де ці залежності збираються, і зручна підміна в тестах. Вбудований `Depends`
FastAPI змішує збирання залежностей з HTTP-шаром і погано працює поза HTTP
(фонові задачі, скрипти).

## Рішення
Використовуємо [dependency-injector](https://python-dependency-injector.ets-labs.org/):
- кореневий `DeclarativeContainer` у `ups_kulka/container.py`;
- контейнер на кожен модуль, підключений через `providers.Container`;
- use cases — `providers.Factory`, спільні ресурси — `providers.Singleton`;
- у роутерах `@inject` + `Depends(Provide["module.use_case"])` з рядковими
  ідентифікаторами;
- у тестах — `provider.override(...)`.

Альтернативи: Dishka (сучасніший, з областями видимості), чистий `Depends`.
Обрано dependency-injector як зрілу бібліотеку з великою спільнотою, на
прохання власника.

## Наслідки
+ Ті самі use cases доступні з HTTP, воркера і CLI.
− Потрібно не забувати `wire()` для нових модулів роутерів — це робить
  `create_app()` автоматично для всіх `modules.*.presentation`.
