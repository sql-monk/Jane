# Handler Runtime

Handler Runtime виконує Python-пакети extractor і transform у контейнерній пісочниці. Він приймає [HandlerInvocation](../../../contracts/schemas/handler-invocation.schema.json) та повертає [HandlerResult](../../../contracts/schemas/handler-result.schema.json) із прив’язкою до входу й точної версії.

## Зміст

- [Межі](#межі)
- [Контекст](#контекст)
- [Навігація](#навігація)

## Межі

Пакет екстрактора містить правила та схеми; Runtime завантажує, перевіряє й запускає їх. CLI з локальним каталогом/ZIP або HTTP із package_archive не потребують Registry. Orchestrator не потрібен для прямого виклику.

Runtime перевіряє manifest/digest, params, input, профіль і output schemas. Він не встановлює довільні бібліотеки під час виклику. Мережа пакета заборонена; access.network=allowlist відхиляється. Пакет не отримує керовані секрети й не записує бізнес-результати в Storage автоматично.

Результат — success/empty/unrecognized/failed. HTTP 200 означає завершений протокольний виклик, включно з status=failed. HTTP problem означає помилку підготовки/доступу/інфраструктури. Own state містить job/results/idempotency; без state_dsn цей стан живе лише у пам’яті.

## Контекст

![Контекст Runtime](../../diagrams/handler-runtime/context.light.png)

[Темна тема](../../diagrams/handler-runtime/context.dark.png) · [Draw.io](../../diagrams/handler-runtime/context.drawio)

Sandbox запускається через Docker API. PostgreSQL опційна для shared state, а не для бізнес-сутностей.

## Навігація

| Сторінка | Що отримати |
|---|---|
| [Швидкий старт](quickstart.md) | Локальний пакет і тести |
| [Залежності](dependencies.md) | Docker, image, профіль та відмови |
| [Конфігурація](configuration.md) | Джерела вмісту, caps, state |
| [Інтеграція](integration.md) | Python/CLI/HTTP без Orchestrator |
| [Будова](internals.md) | Класи, алгоритм, дані й стани |
| [Експлуатація](operations.md) | Моніторинг, оновлення та recovery |
| [HTTP API](reference/api/README.md) | Invoke, test, job та replay |
| [Типи й члени](reference/types/README.md) | Python API та помилки |

Джерела: [ТЗ §4–5](../../../TECHNICAL_SPECIFICATION.md#4-автономність-і-взаємодія), [код](../../../services/handler-runtime/src/jane_handler_runtime/), [handler.v1](../../../contracts/openapi/handler.v1.yaml).
