# jane-kit

`jane-kit` — спільна Python-бібліотека сервісів Jane. Вона дає кожному сервісу однакову поведінку: конфігурацію з успадкуванням лімітів, автентифікацію зі scopes, помилки `application/problem+json`, ідемпотентність, асинхронні job, курсорну пагінацію, health, метрики, журнали й трасування. Код — [libs/jane-kit](../../../libs/jane-kit/), пакет `jane-kit` версії `0.1.0`, Python 3.12+.

## Зміст

- [Межі відповідальності](#межі-відповідальності)
- [Модулі бібліотеки](#модулі-бібліотеки)
- [Сценарії](#сценарії)
- [Автономність](#автономність)
- [Комплект документації](#комплект-документації)

## Межі відповідальності

| Тип | Бібліотека (не сервіс, власного API й процесу не має) |
|---|---|
| Робить | Реалізує спільні конвенції API з [контрактів](../contracts/README.md): `/v1/health`, `/v1/info`, `/metrics`, Problem, `Idempotency-Key`, `202` + job, курсори, `ContentRef`, scopes |
| Не робить | Не містить бізнес-логіки сервісів, не зберігає дані сама: сховища job і ключів ідемпотентності створюють таблиці у **власній** базі сервісу |
| Споживачі | Усі сервіси в `services/` (`dependencies = ["jane-kit"]`), шаблон `templates/service`, тести dev-стеку |

Бібліотека не є довідником контрактів: форму запитів і відповідей визначає [contracts](../contracts/README.md), а `jane-kit` лише реалізує її однаково для всіх сервісів.

## Модулі бібліотеки

| Модуль | Призначення |
|---|---|
| `jane_kit.service` | `create_app` — FastAPI-застосунок зі стандартним підключенням; `run` — запуск uvicorn |
| `jane_kit.config` | `JaneSettings`, моделі `Limits`, злиття рівнів лімітів і `hard_caps` (`resolve_limits`) |
| `jane_kit.auth`, `jane_kit.auth_scopes` | Режими `none` / `api_key` / `jwt`, перевірка scopes, таблиці scopes усіх API |
| `jane_kit.errors` | `JaneError` і підкласи, каталог кодів, обробники помилок FastAPI |
| `jane_kit.idempotency` | `Idempotency-Key`: `idempotent`, `run_idempotent`, сховище в пам'яті |
| `jane_kit.jobs` | `JobRunner`, `Job`, `jobs_router`, правила запису стану job |
| `jane_kit.stores` | Спільні сховища job і ключів ідемпотентності на PostgreSQL і SQLite, оренди та heartbeat |
| `jane_kit.pagination` | `clamp_limit`, `encode_cursor`, `decode_cursor`, `Page` |
| `jane_kit.health`, `jane_kit.metrics` | `/v1/health`, `/v1/info`, `/metrics` (Prometheus) |
| `jane_kit.logs`, `jane_kit.tracing` | JSON-журнали з контекстом, `traceparent` |
| `jane_kit.secrets` | Політика `secret_refs` (`env:`, `file:`), читання файлів секретів, allowlist хостів і origin |
| `jane_kit.content` | Читання й запис `ContentRef` (`inline`, `blob`), транзитні blob на диску |
| `jane_kit.clients` | `ServiceClient` — HTTP-клієнт інших сервісів із повторами й опитуванням job |
| `jane_kit.codegen` | CLI `jane-codegen` — генерація клієнта з OpenAPI |
| `jane_kit.contracts`, `jane_kit.schemas`, `jane_kit.rules` | Валідація за контрактами, контрактний клієнт тестів, моки сусідів, правила колектора |
| `jane_kit.devstack` | Адреси й ключі локального стеку `just up` для інтеграційних тестів |

## Сценарії

- **Новий сервіс.** `just new-service <ім'я>` створює сервіс зі шаблону, який уже використовує `create_app`, ліміти, job та ідемпотентність — [створення сервісу](../../development/new-service.md).
- **Ліміти без зміни коду.** Сервіс оголошує модель `Limits` із безпечними типовими значеннями, а платформа, джерело, завдання й запит їх перекривають — [конфігурація](configuration.md#ліміти).
- **Тривала операція.** Обробник віддає `202` і job, клієнт опитує `GET /v1/jobs/{job_id}` — [інтеграція](integration.md#асинхронні-job).
- **Кілька екземплярів.** Job і ключі ідемпотентності зберігаються у спільних таблицях власної бази сервісу з орендою й fencing — [будова](internals.md#сховища-стану).
- **Виклик іншого сервісу.** `ServiceClient` або клієнт, згенерований `jane-codegen` з контракту — [інтеграція](integration.md#клієнти-інших-сервісів).
- **Контрактні тести.** `ContractClient` перевіряє відповіді справжнього сервісу, `build_mock_app` дає мок сусіда — [інтеграція](integration.md#контрактні-тести-й-моки).

## Автономність

Бібліотека працює без інших модулів Jane: мінімальний сервіс потребує лише Python і залежностей із `pyproject.toml` ([швидкий старт](quickstart.md)). Частина функцій потребує зовнішніх ресурсів:

- `jane_kit.stores.postgres` — PostgreSQL і додаткову залежність `jane-kit[postgres]`;
- `jane_kit.schemas`, `jane_kit.rules`, `jane_kit.contracts` — каталог `contracts/` (у репозиторії або образі);
- режим `jwt` — доступний JWKS постачальника ідентичності.

Повний перелік — [залежності](dependencies.md).

## Комплект документації

| Сторінка | Зміст |
|---|---|
| [quickstart.md](quickstart.md) | Мінімальний сервіс на `jane-kit` і реальні запити |
| [dependencies.md](dependencies.md) | Залежності, версії, поведінка за їх недоступності |
| [configuration.md](configuration.md) | `JaneSettings`, автентифікація, ліміти й `hard_caps`, вбудовані моделі лімітів |
| [integration.md](integration.md) | Використання кожної можливості в сервісі, клієнти, контрактні тести |
| [internals.md](internals.md) | Конвеєр запиту, стани job, алгоритм ідемпотентності, таблиці сховищ |
| [operations.md](operations.md) | Журнали, метрики, health, міграції таблиць, типові проблеми |
| [Довідник типів](reference/types/README.md) | Публічні типи й члени (генерується з коду) |

Загальний індекс довідників — [docs/reference](../../reference/README.md); конвенції API — [contracts](../contracts/README.md); середовище розробки — [docs/development](../../development/README.md).
