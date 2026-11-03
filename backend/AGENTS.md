# backend/AGENTS.md — архітектура бекенду

Спочатку прочитай кореневий [`AGENTS.md`](../AGENTS.md). Тут — точні правила
для коду в `backend/src/ups_kulka/`.

## Структура

```text
src/ups_kulka/
  main.py                 # створення FastAPI-застосунку, lifespan
  container.py            # ЄДИНЕ місце, де збираються залежності (composition root)
  settings.py             # налаштування з env (pydantic-settings)
  shared/
    domain/               # базові Entity, ValueObject, DomainError, Money
    application/          # UnitOfWork-порт, пагінація, базові DTO
    infrastructure/       # БД: engine, Base, SqlAlchemyUnitOfWork
    presentation/         # обробники помилок, спільні HTTP-схеми
  modules/
    <module>/             # catalog, collections, orders, delivery, payments, ...
      domain/             # сутності, value objects, доменні помилки та події
      application/
        ports.py          # Protocol-інтерфейси репозиторіїв і шлюзів
        dto.py            # вхідні/вихідні дані use cases (dataclasses)
        use_cases/        # один файл = один сценарій
        public.py         # (опційно) фасад для інших модулів
      infrastructure/
        tables.py         # SQLAlchemy-моделі (ORM) цього модуля
        repositories.py   # реалізації портів
        mappers.py        # ORM <-> domain
      presentation/
        router.py         # FastAPI-роутер (тонкий!)
        schemas.py        # Pydantic-схеми HTTP (вони формують OpenAPI)
      container.py        # DI-контейнер модуля
```

## Шари і що їм дозволено

| Шар | Можна імпортувати | Не можна |
| --- | --- | --- |
| `domain` | stdlib, `shared.domain` | FastAPI, SQLAlchemy, Pydantic, `application`, `infrastructure`, `presentation`, інші модулі |
| `application` | `domain`, `shared.domain`, `shared.application` | FastAPI, SQLAlchemy, Pydantic, `infrastructure`, `presentation` |
| `infrastructure` | `application`, `domain`, `shared.*`, SQLAlchemy | FastAPI, `presentation` |
| `presentation` | `application` (use cases, DTO), `shared.presentation`, FastAPI, Pydantic, dependency-injector | SQLAlchemy, `infrastructure`, `domain`-сутності напряму у відповіді |
| `container.py` модуля | усе свого модуля | інші модулі (лише через їхній `container` у кореневому `container.py`) |

Між модулями: лише `other_module.application.public`. Перевіряє
`tests/architecture/test_layers.py`.

## Роутер (presentation)

Роутер — це адаптер HTTP. Дозволено рівно три речі:

1. отримати дані запиту (Pydantic-схема, path/query параметри);
2. викликати **один** use case, отриманий через DI;
3. перетворити результат у схему відповіді.

```python
@router.get("/products/{slug}", response_model=ProductOut)
@inject
async def get_product(
    slug: str,
    use_case: GetProduct = Depends(Provide["catalog.get_product"]),
) -> ProductOut:
    product = await use_case(slug)
    return ProductOut.from_dto(product)
```

Заборонено в роутерах: `AsyncSession`, `select(...)`, репозиторії, `if` по
бізнес-правилах, `try/except` для доменних помилок (вони обробляються глобально
в `shared/presentation/errors.py`), обчислення цін і статусів, виклики
зовнішніх сервісів. Тест `test_routers_are_thin` це перевіряє.

## Use case (application)

```python
class CreateProduct:
    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self, cmd: CreateProductCommand) -> ProductDTO:
        async with self._uow_factory() as uow:
            if await uow.products.exists_slug(cmd.slug):
                raise SlugAlreadyTaken(cmd.slug)
            product = Product.create(...)  # правила — в домені
            await uow.products.add(product)
            await uow.commit()
        return ProductDTO.from_entity(product)
```

- Один клас = один сценарій. Назва — дієслово: `CreateProduct`, `PlaceOrder`.
- Приймає команду/запит (dataclass), повертає DTO (dataclass), не ORM і не
  Pydantic.
- Залежить тільки від портів (`Protocol`), ніколи від конкретних класів
  інфраструктури.
- Транзакцію відкриває і комітить use case через UoW. Репозиторії самі не
  комітять.
- Для простого читання (списки для вітрини) дозволений окремий query-порт,
  що одразу повертає DTO (легкий CQRS), — без побудови доменних сутностей.

## Домен

- Сутності й value objects — `dataclass` (frozen для VO), без залежностей.
- Інваріанти перевіряються в конструкторі/фабриці (`Product.create`).
- Помилки — підкласи `DomainError` з кодом (`code = "slug_already_taken"`).
- Гроші — `Money` (копійки, `int`).

## Репозиторій (infrastructure)

- Реалізує порт з `application/ports.py`, приймає `AsyncSession` від UoW.
- Повертає доменні сутності або DTO, **ніколи ORM-об'єкти назовні**.
- Не викликає `commit()` — лише `flush()` за потреби.
- Зв'язки завантажує явно (`selectinload`). У моделях `lazy="raise"`.
- Немає методів, що роблять запит на кожен елемент: замість `get(id)` у циклі —
  `get_many(ids)`.

## DI (dependency-injector)

- Кореневий контейнер `ups_kulka/container.py` створює спільні ресурси
  (settings, engine, session factory, UoW) і підключає контейнери модулів
  через `providers.Container(...)`.
- Контейнер модуля оголошує use cases як `providers.Factory`.
- У роутерах — лише `Depends(Provide["<module>.<use_case>"])` з рядковим
  ідентифікатором (щоб presentation не імпортував контейнер з інфраструктурою).
- У тестах залежності підміняються через `container.<provider>.override(...)`.
- Заборонено: створювати engine/сесії/репозиторії вручну поза контейнером,
  глобальні змінні з сесіями, `container` як service locator усередині use cases.

## Додавання нової функції — порядок кроків

1. `specs/NNN-назва/` — spec → plan (модель даних, індекси, запити) → tasks.
2. Домен + unit-тести.
3. Порти + use case + unit-тести з фейками (`tests/fakes/`).
4. ORM-таблиці + міграція (`make revision m="..."`) + індекси.
5. Репозиторій + інтеграційні тести (включно з `assert_max_queries`).
6. Схеми + роутер + DI-реєстрація + API-тест.
7. `make openapi`, `make check`.
