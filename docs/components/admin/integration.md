# Admin UI: інтеграція

Як адмінка поєднується із сервісами Jane: шляхи через reverse proxy, які операції викликає кожна сторінка, які права потрібні ключу, як замінити сервіс або саму адмінку.

## Зміст

- [Шлях запиту](#шлях-запиту)
- [Сторінки та API](#сторінки-та-api)
- [Операції за сервісами](#операції-за-сервісами)
- [Права ключа](#права-ключа)
- [Самостійне використання](#самостійне-використання)
- [Заміна сервісів](#заміна-сервісів)

## Шлях запиту

![Розгортання Admin UI: браузер, reverse proxy, API сервісів](../../diagrams/admin/deployment.light.png#gh-light-mode-only)
![Розгортання Admin UI: браузер, reverse proxy, API сервісів](../../diagrams/admin/deployment.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/admin/deployment.light.png), [темне](../../diagrams/admin/deployment.dark.png); джерело — [deployment.drawio](../../diagrams/admin/deployment.drawio).

- Браузер завантажує статику й `/config.json` з того самого origin.
- Кожен запит до API — `<api_base>/<сервіс>/v1/...` з `Authorization: Bearer <токен>`. Reverse proxy знімає префікс `/api/<сервіс>` і передає `/v1/...` сервісу. У dev-стеку маршрути задає [Caddyfile](../../../infra/proxy/Caddyfile): `orchestrator`, `registry`, `storage`, `llm`, `handler-runtime`, `assistant`, `web-collector`, `telegram-collector`.
- Токен перевіряє кожен сервіс сам; proxy його не розбирає.
- Окремі виконавці (колектор запуску, виконавець підключення) адресуються за ім'ям із реєстру Orchestrator: `<api_base>/<executor>/v1/...`. Ім'я має відповідати `^[a-z0-9][a-z0-9._-]{0,98}$` і маршруту proxy.

Асинхронні операції повертають `202` і `Job`; адмінка опитує `GET /v1/jobs/{job_id}` того самого сервісу — [будова](internals.md#асинхронні-операції).

## Сторінки та API

![Карта сторінок Admin UI і сервісів, до яких вони звертаються](../../diagrams/admin/pages-api.light.png#gh-light-mode-only)
![Карта сторінок Admin UI і сервісів, до яких вони звертаються](../../diagrams/admin/pages-api.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/admin/pages-api.light.png), [темне](../../diagrams/admin/pages-api.dark.png); джерело — [pages-api.drawio](../../diagrams/admin/pages-api.drawio).

| Сторінка | Маршрут | Сервіси |
|---|---|---|
| Огляд | `/` | Orchestrator, LLM gateway |
| Джерела | `/sources`, `/sources/new`, `/sources/:sourceId` | Orchestrator; Registry (стратегії правил) |
| Завдання | `/tasks`, `/tasks/new`, `/tasks/:taskId` | Orchestrator; Registry (версії етапів) |
| Запуски | `/runs`, `/runs/:runId` | Orchestrator; колектор (помилки збору) |
| Матеріали | `/materials`, `/materials/:materialId/trace` | Storage, Orchestrator |
| Результати | `/results` | Storage; Orchestrator (список підключень) |
| Проблеми | `/problems` | Orchestrator, Storage, Assistant |
| Пакети | `/packages`, `/packages/:packageId` | Registry, Handler Runtime |
| Редактор коду | `/packages/:packageId/versions/:version/edit` | Registry |
| Редактор правил колектора | `/packages/:packageId/versions/:version/rules` | Registry |
| Асистент | `/assistant` | Assistant, Orchestrator |
| Підключення | `/connections` | Orchestrator; виконавець за ім'ям |
| LLM | `/llm` | LLM gateway |
| Ліміти | `/limits` | Orchestrator |
| Аудит | `/audit` | Orchestrator |
| Вхід | `/login`, `/auth/callback` | постачальник OIDC (за `oidc`) |

## Операції за сервісами

Шляхи наведено без префікса `<api_base>/<сервіс>`. Повний опис операцій — у довідниках API сервісів.

### Orchestrator

| Операція | Сторінки |
|---|---|
| `GET /v1/sources`, `POST /v1/sources` | Огляд, Джерела, Асистент (створення з чернетки) |
| `GET`, `PUT`, `DELETE /v1/sources/{source_id}` | Джерело, Версії етапів |
| `GET /v1/tasks`, `POST /v1/tasks` | Огляд, Завдання, Проблеми (прив'язки пакета), Асистент |
| `GET`, `PUT`, `DELETE /v1/tasks/{task_id}` | Завдання |
| `POST /v1/task-validations` | Завдання — «Перевірити в оркестраторі» |
| `POST /v1/tasks/{task_id}/runs` | Завдання, Огляд — «Запустити» |
| `GET`, `POST /v1/tasks/{task_id}/stages/{stage_id}/activations` | Завдання — «Версії етапів» |
| `GET /v1/runs`, `GET /v1/runs/{run_id}`, `GET /v1/runs/{run_id}/items` | Огляд, Запуски, Завдання |
| `POST /v1/runs/{run_id}/cancel` | Запуски — «Зупинити», «Скасувати запуск» |
| `POST /v1/reprocessing` | Запуски, Матеріали, Проблеми — повторна обробка |
| `GET /v1/materials/{material_id}/trace` | Матеріали — «Простежити» |
| `GET /v1/problem-groups`, `PATCH /v1/problem-groups/{group_id}` | Огляд, Проблеми |
| `GET /v1/unknown-materials` | Проблеми — «Невідомі матеріали» |
| `GET /v1/executors` | Огляд, Запуски |
| `GET /v1/connections`, `GET`, `PUT`, `DELETE /v1/connections/{connection_id}` | Підключення; вибір сховища на сторінках Матеріали, Результати, Проблеми |
| `GET`, `PUT /v1/limits/platform`, `GET /v1/limits/effective` | Ліміти, Джерело, Завдання |
| `GET /v1/audit-events` | Аудит |

### Registry

| Операція | Сторінки |
|---|---|
| `GET /v1/packages`, `POST /v1/packages` | Пакети, Версії етапів (форки) |
| `GET`, `PATCH /v1/packages/{package_id}` | Пакет — «Огляд» |
| `GET`, `POST /v1/packages/{package_id}/versions` | Пакет, Версії етапів, публікація з редакторів |
| `GET /v1/packages/{package_id}/versions/{version}` | Пакет, редактори, стратегії джерела |
| `GET /v1/packages/{package_id}/versions/{version}/file` | редактор коду (читання файлів) |
| `POST /v1/packages/{package_id}/versions/{version}/status` | Пакет — «Погодити», «Відхилити», «Застаріла», «Відкликати (yank)» |
| `GET /v1/packages/{package_id}/diff` | Пакет — «Відмінності», «Оновлення батька» |
| `POST /v1/packages/{package_id}/forks` | Пакет — «Створити форк» |
| `GET /v1/packages/{package_id}/upstream`, `POST …/upstream-ports` | Пакет — «Оновлення батька» |
| `GET /v1/jobs/{job_id}` | перенесення змін батька |

### Storage

| Операція | Сторінки |
|---|---|
| `GET /v1/objects`, `GET /v1/objects/{object_id}` | Матеріали, Проблеми (RAW прикладів) |
| `GET /v1/objects/{object_id}/content` з `Range: bytes=0-<preview_max_bytes-1>` | Матеріали — «Переглянути» |
| `GET /v1/entities`, `GET /v1/entity-history` | Результати |

### LLM gateway

| Операція | Сторінки |
|---|---|
| `GET /v1/providers`, `GET`, `PUT /v1/providers/{provider_id}` | LLM — «Провайдери й моделі» |
| `GET /v1/model-aliases`, `PUT /v1/model-aliases/{alias}` | LLM — «Псевдоніми моделей» |
| `GET /v1/budgets`, `PUT`, `DELETE /v1/budgets/{scope_type}/{scope_id}` | LLM — «Бюджети» |
| `GET /v1/usage` | LLM — «Витрати», Огляд |

### Handler Runtime і виконавці

| Операція | Сервіс | Сторінки |
|---|---|---|
| `POST /v1/test-runs`, `GET /v1/jobs/{job_id}`, `POST /v1/jobs/{job_id}/cancel` | Handler Runtime (`services.handler`) | Пакет — «Запустити тести (без запису)» |
| `POST /v1/connections/{connection_id}/test` | виконавець за ім'ям із `executors` підключення | Підключення — «Перевірити» |
| `GET /v1/collections/{collection_id}/errors` | колектор із роллю `collector` у `GET /v1/executors`, інакше `services.collector` | Запуск — «Помилки колектора» |

### Assistant

| Операція | Сторінки |
|---|---|
| `GET /v1/info` | Асистент — «Ліміти дослідження» |
| `GET`, `POST /v1/onboarding-sessions`, `GET /v1/onboarding-sessions/{session_id}` | Асистент — «Підключення джерел» |
| `POST …/{session_id}/candidate-selection`, `POST …/{session_id}/proposals/{proposal_id}/acceptance` | Асистент — «Обрати», «Прийняти варіант» |
| `GET`, `POST /v1/improvement-runs` | Асистент — «Запуски вдосконалення», Проблеми — «Запустити вдосконалення» |
| `GET /v1/jobs/{job_id}`, `POST /v1/jobs/{job_id}/cancel` | панелі job асистента |

Заголовки: створення (`POST` джерел, завдань, пакетів, версій, форків, запусків, тестів, активацій, сесій) надсилає новий `Idempotency-Key` на кожну дію користувача; `PUT`/`PATCH` ресурсів з `ETag` надсилають `If-Match`; `PATCH` — `Content-Type: application/merge-patch+json`. Правила — [contracts/README.md](../../../contracts/README.md) і довідники API.

## Права ключа

Ключ адміністратора dev-стеку має такі області (`scopes`) у [infra/compose.yaml](../../../infra/compose.yaml); власний ключ для іншого розгортання потребує тих самих, щоб працювали всі сторінки.

| Сервіс | Області ключа `admin` |
|---|---|
| Orchestrator | `orchestrator:read`, `orchestrator:write`, `orchestrator:admin` |
| Registry | `registry:read`, `registry:write`, `registry:approve` |
| Storage | `storage:read`, `handler:invoke`, `handler:test`, `connections:write` |
| Handler Runtime | `handler:invoke`, `handler:test`, `connections:write` |
| LLM gateway | `llm:invoke`, `llm:admin`, `handler:invoke`, `handler:test`, `connections:write` |
| Assistant | `assistant:use` |
| Web Collector, Telegram Collector | `collector:read`, `collector:run`, `connections:write` |

Без потрібної області сервіс повертає `403 forbidden`, і адмінка показує це на відповідній дії. Для режиму `oidc` області мають прийти в claim `scope` токена.

## Самостійне використання

Admin UI — окремий клієнт. Йому потрібні лише сумісні API за префіксами proxy, тому:

- **без сервісів Jane** адмінка працює на контрактних моках ([швидкий старт](quickstart.md#запуск-на-моках));
- **з частиною сервісів** працюють сторінки, чиї API доступні; решта показує помилки;
- **сторонній застосунок** не вбудовує адмінку, а викликає ті самі API напряму через proxy. Приклад — запит, який робить сторінка «Джерела» (PowerShell; адреса й ключ — з `just env`):

  ```powershell
  (Invoke-WebRequest -Uri "$env:JANE_STACK_PROXY_URL/api/orchestrator/v1/sources?limit=50" -Headers @{ Authorization = "Bearer $env:JANE_STACK_AUTH_ADMIN_API_KEY" }).Content
  ```

  Bash:

  ```bash
  curl -s -H "Authorization: Bearer $JANE_STACK_AUTH_ADMIN_API_KEY" "$JANE_STACK_PROXY_URL/api/orchestrator/v1/sources?limit=50"
  ```

  Відповідь на порожньому стеку (перевірено на стеку `jane-doc-ui`):

  ```json
  {"items":[],"next_cursor":null}
  ```

  Змінні `JANE_STACK_*` у сесії оболонки потрібно задати самостійно зі значень `just env`.

Пакет `@jane/admin` приватний (`"private": true`): клієнти з `src/api` не публікуються як бібліотека. Сторонньому TypeScript-застосунку краще згенерувати власні типи з `contracts/openapi` тим самим `openapi-typescript`.

## Заміна сервісів

- **Сервіс** можна замінити реалізацією того самого контракту `/v1`: адмінка залежить лише від шляхів, схем і моделі помилок `problem+json`. Маршрут proxy має вести на нову реалізацію; якщо змінилося ім'я сегмента — змініть `services.<ключ>` у `config.json`.
- **Окремий сервіс у розробці** підставляється замість мока змінною `JANE_ADMIN_TARGET_<API>` ([configuration.md](configuration.md#змінні-dev-сервера)).
- **Сама адмінка** замінюється будь-яким клієнтом тих самих API; власних даних, які треба переносити, у неї немає.
