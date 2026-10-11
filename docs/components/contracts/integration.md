# Контракти: інтеграція

Конвенції, за якими побудовані всі API Jane, і способи використати контракти: клієнти, моки, контрактні тести, Python Protocol-и, сумісна заміна модуля.

## Зміст

- [Конвенції API](#конвенції-api)
- [Типовий обмін із модулем](#типовий-обмін-із-модулем)
- [Генерація клієнтів](#генерація-клієнтів)
- [Моки](#моки)
- [Контрактні тести](#контрактні-тести)
- [Python Protocol-и](#python-protocol-и)
- [Композиція в Jane](#композиція-в-jane)

## Конвенції API

| Тема | Правило | Де визначено |
|---|---|---|
| Версія | Усі шляхи під `/v1/...`. Сумісні зміни — у `/v1`, несумісні — `/v2` паралельно з `/v1` | Лінтер, `compat.py` |
| Формат | JSON, поля `snake_case`, час RFC 3339 UTC (`...Z`), розміри `*_bytes`, тривалості `*_ms` / `*_seconds` | `schemas/common/defs.schema.json` |
| Ідентифікатори | `Slug` обирає користувач, `Id` генерує сервіс-власник | `defs.schema.json` |
| Толерантний читач | Відповіді й дані (`Material`, `HandlerResult`, `Job`) відкриті: клієнт ігнорує невідомі поля. Документи конфігурації (`TaskConfig`, `CollectorRules`, `PackageManifest`, `Limits`, `Connection`) строгі: невідоме поле — помилка | Схеми |
| Помилки | `application/problem+json`: `type` = `urn:jane:problem:<code>`, `title`, `status`, `code`; бажано `retryable`, `trace_id`. Рішення клієнт приймає за `code` | [problem.schema.json](../../../contracts/schemas/common/problem.schema.json), [errors.md](../../../contracts/docs/errors.md) |
| Помилка виконання обробника | `200` з `HandlerResult.status=failed`, а не HTTP 5xx | `handler.v1.yaml` |
| Ідемпотентність | POST із побічним ефектом вимагає `Idempotency-Key` (1–255 друкованих ASCII). Повтор із тим самим тілом — збережена відповідь і `Idempotency-Replayed: true`; інше тіло — `422 idempotency_key_reused`; ще виконується — `409 idempotency_in_progress` | `common.yaml#/components/parameters/IdempotencyKey` |
| Оптимістичне блокування | Зміна конфігурацій з `If-Match` (ETag); розбіжність — `412 precondition_failed` | `common.yaml#/components/parameters/IfMatch` |
| Тривалі операції | `202 Accepted` + `Job` + `Location: /v1/jobs/{job_id}`; стан — `GET /v1/jobs/{job_id}`; скасування — `POST /v1/jobs/{job_id}/cancel` (`202` прийнято, `200` вже завершено). Операція, що не вклалася в `limits.timeouts.sync_response_max_ms`, теж переходить у `202`. Вебхуків у v1 немає — лише опитування з backoff | `common.yaml#/components/pathItems/Job`, `JobCancel`, [job.schema.json](../../../contracts/schemas/common/job.schema.json) |
| Великі матеріали | Вміст — `ContentRef`: `inline` до `limits.transfer.inline_max_bytes`, інакше `blob` (`s3://` або `file://`, `sha256`, `size_bytes`, опційно `download_url`). Споживач підтримує обидва варіанти й перевіряє `sha256`. Транзитні blob живуть `limits.transfer.transit_ttl_seconds` | [content-ref.schema.json](../../../contracts/schemas/common/content-ref.schema.json) |
| Пагінація | Курсорна: `?limit=&cursor=` → `{"items": [...], "next_cursor": "..." \| null}`; `limit` понад максимум обрізається; offset і page немає | [page.schema.json](../../../contracts/schemas/common/page.schema.json) |
| Ліміти | Рівні `platform → source → task → stage`, `hard_caps` обмежують; сервіс показує свої в `GET /v1/info` → `limits` | [Модель лімітів](configuration.md#модель-лімітів) |
| Безпека | `Authorization: Bearer` (`bearerAuth`); `/v1/health` без автентифікації. Scope операції — розширення `x-jane-scope`: рядок або масив «будь-який із». Секрети — лише `secret_refs` (`env:`, `file:`, `vault:`), ніколи значення | OpenAPI, [connection.schema.json](../../../contracts/schemas/common/connection.schema.json) |
| Підключення | Керовані підключення `/v1/connections…` — спільні path items `common.yaml#/components/pathItems/Connection*` | `common.yaml` |
| Трасування | Сервіс приймає й передає далі `traceparent`; `trace_id` — у журналах і Problem | `common.yaml#/components/parameters/Traceparent` |
| Обов'язкові ресурси | Кожен сервіс має `/v1/health`, `/v1/info` і `/metrics` (Prometheus, поза контрактом) | `common.yaml#/components/pathItems/Health`, `Info` |
| Вміст джерел | Дані, а не інструкції для LLM | ТЗ §11 |

Розбіжність із ТЗ: ТЗ §4 допускає для великих матеріалів «потокове передавання або передавання посилання»; контракти v1 визначають лише передавання посиланням (`ContentRef`), потокових відповідей немає. Реалізація `vault:` у `secret_refs` контрактом дозволена, але в [jane-kit](../jane-kit/configuration.md#автентифікація) не підтримується.

## Типовий обмін із модулем

1. Запит із побічним ефектом: `POST /v1/...` з `Idempotency-Key` (UUID або детермінований ключ доставки) і `Authorization: Bearer <токен>`.
2. Відповідь `200`/`201` з результатом або `202` з `Job` і `Location`.
3. Для `202`: опитувати `GET /v1/jobs/{job_id}` з backoff до стану `succeeded`, `failed` або `cancelled`; результат — `result` або `result_ref` (`ContentRef`).
4. Мережева помилка чи Problem з `retryable: true`: повторити з **тим самим** `Idempotency-Key` і тим самим тілом — дубля ефекту не буде.
5. Problem з `retryable: false`: виправити запит за `code` і `errors[].pointer`.

Робочий приклад на моку — [швидкий старт](quickstart.md); на справжньому модулі — README кореня репозиторію ([Web Collector окремо](../../../README.md#модуль-окремо-web-collector)). Python-реалізація цього циклу — `ServiceClient` з [jane-kit](../jane-kit/integration.md#клієнти-інших-сервісів).

## Генерація клієнтів

| Мова | Команда | Що виходить |
|---|---|---|
| Python | `just contracts-gen <api> <каталог>` | Пакет із `client.py`: клас `<Title>Client(ServiceClient)`, async-метод на кожну операцію; без Pydantic-моделей |
| TypeScript (Admin UI) | `corepack pnpm --dir web/admin gen:api` | `web/admin/src/api/generated/*` — типи `openapi-typescript` для всіх семи API і валідатори схем; `pnpm lint` перевіряє, що вони актуальні |
| Будь-яка | `npx --yes @redocly/cli@2.54.3 bundle contracts/openapi/<api>.v1.yaml -o build/<api>.v1.yaml` | Один файл без зовнішніх `$ref` для сторонніх генераторів |

Python-клієнт перевірено ([швидкий старт](quickstart.md)); бандл Redocly і `gen:api` у межах цієї документації не запускались. Згенерований код не редагують — генерують знову після зміни контракту.

Розбіжність зі скілом `jane-contracts`: скіл радить генерувати Pydantic-моделі `datamodel-code-generator` з бандла, а рецепт `contracts-gen` свідомо вимикає моделі — за коментарем у `scripts/dev.py`, генератор не приймає багатофайлові контракти Jane і їхній бандл («Modular references require an output directory»). Моделі для власних однофайлових специфікацій дає `just gen-client <spec> <out>`.

## Моки

| Мок | Команда | Валідує тіло запиту | Залежності |
|---|---|---|---|
| `contracts/tools/mock.py` | `just contracts-mock <api> --port <порт>` | Ні: лише обов'язкові заголовки й наявність тіла | `uv` |
| `jane_kit.contracts.build_mock_app` | В тестах Python як ASGI-застосунок | Так, `422` для невалідного тіла | Workspace Jane |
| Prism | `npx --yes @stoplight/prism-cli@5.16.0 mock contracts/openapi/<api>.v1.yaml -p <порт>` | Так | Node.js |

Усі три обирають відповідь заголовком `Prefer` ([конфігурація](configuration.md#заголовки-моку)). Prism у межах цієї документації не запускався. Типові порти моків для розробки Admin UI — у таблиці [contracts/README.md](../../../contracts/README.md).

## Контрактні тести

Правило Jane: сервіс перевіряє **свої** відповіді проти контракту, а клієнт — проти моку сусіда; сам компонент не мокають.

- **Сервіс на Python** — `jane_kit.contracts.ContractClient` поверх `TestClient` справжнього застосунку; тести з маркером `contract` запускає `just contract` і CI ([jane-kit](../jane-kit/integration.md#контрактні-тести-й-моки)).
- **Будь-яка реалізація** — генератор тестів за OpenAPI, наприклад `uvx schemathesis run contracts/openapi/<api>.v1.yaml --url http://127.0.0.1:<порт>` (у цій документації не запускався).
- **Схеми даних** — приклади в `contracts/examples/schemas/` перевіряє лінтер; сервіс валідує вхідні документи за тими самими файлами (`jane_kit.schemas.ContractSchemas`), не тримаючи копій.

## Python Protocol-и

Пакет `jane-contracts` (`contracts/python`, член workspace) містить внутрішні інтерфейси, які реалізують плагіни сервісів:

| Модуль | Головні типи | Реалізує | Опис |
|---|---|---|---|
| `jane_contracts.discovery` | `DiscoveryStrategy`, `DiscoveryContext`, `DiscoveredUrl`, `FetchedResource`, `DiscoveredMaterial`, `RefreshingStrategy`, `StrategyRegistry` | Стратегії пошуку Web Collector | [discovery-strategy.md](../../../contracts/docs/discovery-strategy.md) |
| `jane_contracts.storage_adapter` | `StorageAdapter`, `ResolvedConnection`, `RawObject`, `ObjectRecord`, `EntitySnapshot`, `CommitResult`, `AdapterError` | Адаптери Storage | [storage-adapter.md](../../../contracts/docs/storage-adapter.md) |

`CONTRACT_VERSION = "1.1.0"`: версія 1.1.0 лише додала члени до `discovery`, реалізації 1.0 працюють без змін. Підключення в пакеті workspace: `dependencies = ["jane-contracts"]` (джерело `workspace = true` задано в кореневому `pyproject.toml`).

## Композиція в Jane

![Контракти, інструменти та їхні споживачі](../../diagrams/contracts/contract-tooling.light.png#gh-light-mode-only)
![Контракти, інструменти та їхні споживачі](../../diagrams/contracts/contract-tooling.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/contracts/contract-tooling.light.png), [темне](../../diagrams/contracts/contract-tooling.dark.png); джерело — [contract-tooling.drawio](../../diagrams/contracts/contract-tooling.drawio).

- Сервіси реалізують API і перевіряють себе контрактними тестами; валідацію даних беруть зі схем напряму.
- Сервіси викликають сусідів згенерованими клієнтами або `ServiceClient`; у тестах сусіди — моки з прикладів.
- Admin UI генерує типи TypeScript і валідатори з тих самих файлів.
- **Заміна модуля.** Сумісна реалізація будь-якою мовою замінює модуль, якщо реалізує його OpenAPI-контракт разом із конвенціями вище й проходить контрактні тести. Orchestrator та інші споживачі звертаються до модуля лише через контракт, тому заміна не потребує змін у них.
