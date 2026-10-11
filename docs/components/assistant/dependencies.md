# Assistant: залежності

Сусіди Assistant, його стан і пошук джерел: які операції кожного використовуються, що обов'язкове для якої функції та що відбувається за недоступності. Факти звірено з `services/assistant/src/jane_assistant/clients.py`, `settings.py`, `infra/compose.yaml` і `services/assistant/pyproject.toml` ревізії `48389a3`.

## Зміст

- [Схема сусідів](#схема-сусідів)
- [Огляд](#огляд)
- [Середовище виконання](#середовище-виконання)
- [LLM gateway](#llm-gateway)
- [Колектори](#колектори)
- [Handler Runtime](#handler-runtime)
- [Registry](#registry)
- [Orchestrator](#orchestrator)
- [Storage](#storage)
- [Пошуковий провайдер](#пошуковий-провайдер)
- [Стан і схеми контрактів](#стан-і-схеми-контрактів)
- [Загальна поведінка за недоступності](#загальна-поведінка-за-недоступності)

## Схема сусідів

![Assistant і сусіди: обов'язкові й опційні залежності](../../diagrams/assistant/context.light.png#gh-light-mode-only)
![Assistant і сусіди: обов'язкові й опційні залежності](../../diagrams/assistant/context.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/assistant/context.light.png), [темне](../../diagrams/assistant/context.dark.png); джерело — [context.drawio](../../diagrams/assistant/context.drawio).

Суцільна лінія — сусід, без якого не працює щонайменше одна операція; штрихова — опційний сусід; пунктир — власні дані. Assistant лише викликає API сусідів і не читає їхніх таблиць.

## Огляд

| Сусід | Змінна адреси | Підключення джерела | Вдосконалення | Невідомий матеріал |
|---|---|---|---|---|
| LLM gateway | `JANE_ASSISTANT_LLM_URL` | обов'язковий | обов'язковий | обов'язковий |
| Web Collector, Telegram Collector | `JANE_ASSISTANT_COLLECTOR_WEB_URL`, `…_COLLECTOR_TELEGRAM_URL` | обов'язковий для типу джерела | — | — |
| Handler Runtime | `JANE_ASSISTANT_HANDLER_RUNTIME_URL` | обов'язковий (тести) | обов'язковий | — |
| Registry | `JANE_ASSISTANT_REGISTRY_URL` | пошук готових пакетів — опційно; прийняття — обов'язково | обов'язковий | — |
| Orchestrator | `JANE_ASSISTANT_ORCHESTRATOR_URL` | опційний: активація | опційний: прив'язки, групи проблем, активація | опційний: очікувані типи сутностей |
| Storage | `JANE_ASSISTANT_STORAGE_URL` | — | опційний: зразки `material_ref` | — |
| Пошуковий провайдер | `JANE_ASSISTANT_SEARCH_PROVIDER` | опційний: пошук за назвою | — | — |
| PostgreSQL | `JANE_ASSISTANT_STATE_DSN` | опційний: кілька екземплярів | те саме | те саме |

Сусід без адреси вважається ненастроєним: його наявність показує `GET /v1/info` → `capabilities.neighbours`. Розбіжність із [contracts/docs/data-ownership.md](../../../contracts/docs/data-ownership.md): там Orchestrator названо потрібним «лише для автоактивації», а в коді він також дає прив'язки пакета, оновлює групи проблем і уточнює очікувані типи сутностей.

## Середовище виконання

| Компонент | Версія | Джерело |
|---|---|---|
| Python | `>=3.12` | `services/assistant/pyproject.toml` |
| jane-kit | з workspace | `[tool.uv.sources]` |
| psycopg[binary,pool] | `>=3.2` | стан у PostgreSQL |
| Образ Docker | `python:3.12-slim`, uv `0.12.13`; у образ копіюються `contracts/schemas` | `services/assistant/Dockerfile` |

## LLM gateway

Операції: `POST /v1/completions` — завжди зі `output_schema`, `temperature: 0`, `scope.purpose` (`onboarding`, `improvement`, `unknown_material`), `scope.run_id` запуску й `limits.llm` з бюджетом запуску; для `JANE_ASSISTANT_LLM_COMPLETION_MODE=async` — також `GET /v1/jobs/{job_id}`. Моделі обираються псевдонімами `cheap` (класифікація) і `strong` (аналіз, варіанти, код) — їх треба створити в шлюзі. Документація шлюзу — [LLM gateway](../llm/README.md).

| Ситуація | Результат |
|---|---|
| адресу не задано | job завершується `failed`, `upstream_unavailable`: `llm is not configured for the assistant` |
| псевдонім не налаштовано | шлюз повертає 404; job — `failed`, `upstream_unavailable`: `LLM request failed: HTTP 404: not_found` (перевірено в [quickstart.md](quickstart.md#невідомий-матеріал)) |
| бюджет вичерпано (429 `budget_exhausted` або вичерпано бюджет запуску) | підключення: `insufficient_sample` з причиною; вдосконалення: `unresolved`; невідомий матеріал: порада `none` з поясненням `not analysed` |
| шлюз недоступний, 5xx | повтори за `clients.retries`, далі `upstream_unavailable` і `failed` |
| вихід моделі не відповідає схемі | генерація екстрактора й вдосконалення — нова спроба з відгуком; інші кроки — `failed` з `schema_mismatch` |

Тайм-аут одного синхронного запиту — `llm_call.request_timeout_ms` (типово 15 хвилин), бо генерація може тривати хвилини.

## Колектори

Операції `collector.v1`: `POST /v1/collections` (обмежений збір вибірки), `GET /v1/collections/{id}/materials` (довге опитування), `POST /v1/jobs/{id}/cancel` (зупинка збору після вибірки), `POST /v1/rules/validations` (перевірка правил кожного варіанта). Колектор обирається за типом джерела: `web` або `telegram`. Документація — [Web Collector](../web-collector/README.md), [Telegram Collector](../telegram-collector/README.md).

| Ситуація | Результат |
|---|---|
| колектор потрібного типу не налаштовано | сесія `failed`, `upstream_unavailable`: `collector is not configured for the assistant` (перевірено в [quickstart.md](quickstart.md#недоступний-сусід)) |
| збір не завершився після `onboarding.max_empty_polls` порожніх опитувань поспіль | `insufficient_sample`: різноманітність матеріалів не підтверджено |
| колектор відхилив правила варіанта | варіант відкидається; якщо не лишилося жодного, Assistant будує запасний варіант з правил вибірки |

## Handler Runtime

Операція `handler.v1`: `POST /v1/test-runs` з чернеткою пакета в `package_archive` (inline, до `transfer.inline_max_bytes`) або з посиланням на опубліковану версію, і очікування job. Тести ніколи не пишуть у робочі дані. Документація — [Handler Runtime](../handler-runtime/README.md).

| Ситуація | Результат |
|---|---|
| адресу не задано | `upstream_unavailable`: підключення зупиняється на аналізі, вдосконалення — одразу |
| job тест-прогону `failed` | `upstream_unavailable` (якщо помилка повторювана) або `conflict`; job Assistant — `failed` |
| архів чернетки більший за `transfer.inline_max_bytes` | під час підключення пакет лишається неперевіреним, і це ризик варіанта; під час вдосконалення — `payload_too_large` |

## Registry

Операції `registry.v1`: пошук пакетів (`GET /v1/packages` за `kind`, `entity_type`, `domain`), картка й архів версії, створення пакета, публікація версії, статус (`approved`), запис результатів тестів, форк. Усі записи мають детерміновані `Idempotency-Key` від job, тому повтор не створює дублікатів. Документація — [Registry](../registry/README.md).

| Ситуація | Результат |
|---|---|
| адресу не задано під час аналізу | готові екстрактори не шукаються; для кожного типу сутності створюється новий пакет |
| адресу не задано під час прийняття або вдосконалення | `upstream_unavailable`, job `failed` |
| пакет уже існує (409 на створення) | використовується наявний |
| дайджест архіву не збігся з `ETag` | `digest_mismatch` |

## Orchestrator

Операції `orchestrator.v1`: `POST /v1/sources` і `POST /v1/tasks` (активація під час прийняття), `GET /v1/tasks?package_id=` і `GET /v1/tasks/{id}` (прив'язки пакета), `POST /v1/tasks/{id}/stages/{stage}/activations` (автоактивація й відкат), `PATCH /v1/problem-groups/{id}` (стан групи проблем), `GET /v1/sources/{id}` (очікувані типи сутностей). Документація — [Orchestrator](../orchestrator/README.md).

| Ситуація | Результат |
|---|---|
| адресу не задано, прийняття з `activate: true` | `activated: false`, повертаються чернетки джерела й завдання |
| адресу не задано, вдосконалення | прив'язки — лише з запиту, без параметрів етапів; група проблем не оновлюється; автоактивації немає |
| групу проблем не вдалося оновити | попередження в журналі, запуск триває |
| джерело не прочиталося під час аналізу невідомого матеріалу | попередження в журналі; порада без урахування очікуваних типів |
| Orchestrator відхилив активацію на одній із прив'язок | уже виконані активації відкочуються, `activated: false` |

## Storage

Операції `storage.v1`: `GET /v1/objects/{object_id}` і `GET /v1/objects/{object_id}/content` для зразків, переданих як `material_ref` (`storage_connection_id`, `object_id`). Документація — [Storage](../storage/README.md).

| Ситуація | Результат |
|---|---|
| адресу не задано, зразок — `material_ref` | `upstream_unavailable`, job `failed`; зразок можна передати inline як `material` |
| об'єкт без метаданих матеріалу й не є збереженим документом `Material` | `not_implemented`: передайте зразок inline |

## Пошуковий провайдер

Перетворює назву сайту чи каналу на кандидатів. URL, `@канал` і `t.me/<канал>` пошуку не потребують.

| `JANE_ASSISTANT_SEARCH_PROVIDER` | Джерело кандидатів |
|---|---|
| `none` (типово) | пошуку немає: назва дає `validation_failed` (`no search provider configured; give an exact URL or @channel`) |
| `static` | JSON-каталог `JANE_ASSISTANT_SEARCH_STATIC_FILE` |
| `http_json` | HTTP-ендпоінт `JANE_ASSISTANT_SEARCH_URL_TEMPLATE` з `{query}` |

Без кандидатів сесія завершується `failed` з `not_found`. Параметри — [configuration.md](configuration.md#пошук-джерел).

## Стан і схеми контрактів

- **PostgreSQL** (`JANE_ASSISTANT_STATE_DSN`) — сесії, job і ключі ідемпотентності кількох екземплярів. Без нього стан у пам'яті одного процесу й зникає під час перезапуску. У dev-стеку — `postgres:18`; на ньому пройшли інтеграційні тести `just integration --project jane-doc-llm services/assistant` (9 тестів, 2026-10-11). Недоступна база під час старту зупиняє старт; під час роботи перевірка `state` у `/v1/health` стає `down`.
- **`contracts/schemas`** — локальна перевірка згенерованих правил, маніфестів і матеріалів. Каталог шукається вгору від пакета (checkout) або в `/app/contracts` (образ Docker); явно — `JANE_ASSISTANT_CONTRACTS_DIR`. Якщо каталог не знайдено, `capabilities.local_schema_validation` — `false` і локальні перевірки за схемами пропускаються; перевірка правил колектором (`validateRules`) лишається.

## Загальна поведінка за недоступності

- Ненастроєний сусід не вгадується: операція, якій він потрібен, завершується `upstream_unavailable` з назвою сусіда. Інші операції працюють.
- Виклики сусідів повторюються за `clients.retries` (контракт `retries`) з тайм-аутами `clients.*`; виклики LLM — з власним тайм-аутом `llm_call.request_timeout_ms`.
- Помилка всередині job не губиться: сесія підключення отримує `status: failed` і `error` з моделлю помилки, job — `failed` з `error`.
- Записи в Registry й Orchestrator ідемпотентні, тож повторний запуск після збою не створює дублікатів пакетів, версій, джерел чи завдань.
