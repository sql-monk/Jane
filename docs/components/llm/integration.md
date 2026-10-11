# LLM gateway: інтеграція

Як викликати LLM gateway зі стороннього застосунку, як виконувати LLM-пакети, керувати бюджетами, підключити Anthropic, як шлюз працює в складі Jane і як його замінити сумісною реалізацією. Приклади виконано 2026-10-11 на Windows 11 (Git Bash, `curl`) з провайдером `fake`, ревізія `48389a3`; сервіс слухав інший порт, у командах — типовий `8110`.

## Зміст

- [Запит до моделі](#запит-до-моделі)
- [Асинхронний запит](#асинхронний-запит)
- [Помилки](#помилки)
- [Бюджети й облік](#бюджети-й-облік)
- [LLM-пакети](#llm-пакети)
- [Сценарні відповіді fake](#сценарні-відповіді-fake)
- [Підключення Anthropic](#підключення-anthropic)
- [Композиція в Jane](#композиція-в-jane)
- [Заміна сумісною реалізацією](#заміна-сумісною-реалізацією)

## Запит до моделі

`POST /v1/completions` (дозвіл `llm:invoke`, заголовок `Idempotency-Key` обов'язковий). Тіло — `CompletionRequest`:

| Поле | Обов'язкове | Зміст |
|---|---|---|
| `instructions` | так | довірені інструкції; потрапляють лише в системний канал моделі |
| `data[]` | ні | недовірені дані: `name`, `media_type`, `text` або `content` (об'єкт); обгортаються розмежувачами |
| `output_schema` | ні | JSON Schema відповіді; без неї відповідь — `output_text` |
| `model` | ні | псевдонім (`default`, якщо не задано) або `provider_id/model_id` |
| `max_output_tokens`, `temperature`, `max_schema_retries` | ні | параметри виклику в межах лімітів |
| `scope` | так | `purpose` (`handler`, `onboarding`, `improvement`, `unknown_material`, `other`) і опційні `source_id`, `task_id`, `run_id` — рівні бюджету й облік |
| `limits` | ні | `limits.llm` запиту (див. [configuration.md](configuration.md#ліміти-в-запиті)) |
| `test_mode` | ні | позначка в обліку `usage` |
| `mode` | ні | `sync` (типово) або `async` |

Дані ніколи не змішуються з інструкціями: текст сторінок і повідомлень, навіть якщо він містить «ignore previous instructions», модель отримує лише як дані. Механізм — [internals.md](internals.md#розділення-інструкцій-і-даних).

Приклад запиту й відповіді — [quickstart.md](quickstart.md#кроки), крок 3. Поля відповіді `CompletionResult`:

| Поле | Зміст |
|---|---|
| `completion_id` | ідентифікатор запиту (`cmp_…`) |
| `model` | фактичні `provider_id` і `model_id` |
| `valid`, `validation_errors[]` | чи відповідає вихід `output_schema` і що не так (JSON Pointer) |
| `output` або `output_text` | розібраний JSON за валідної схемної відповіді, інакше текст моделі |
| `finish_reason` | `stop`, `length`, `content_filter` |
| `usage` | токени й вартість усіх спроб разом |
| `budget[]` | стан кожного застосованого бюджету: `spent`, `limit`, `exhausted`, `resets_at` |

## Асинхронний запит

З `"mode": "async"` шлюз одразу повертає 202 і job; результат — у `GET /v1/jobs/{job_id}`. Так клієнт не тримає довге з'єднання на час генерації.

```bash
curl -s -X POST http://127.0.0.1:8110/v1/completions -H 'Content-Type: application/json' -H 'Idempotency-Key: quickstart-3' -d '{"instructions": "Say hi.", "mode": "async", "scope": {"purpose": "other"}}'
```

```json
{"job_id": "job_ed7037948e5d4618b3df443892384f32", "kind": "llm_completion", "status": "queued", "created_at": "2026-10-11T09:57:39.166684Z", "idempotency_key": "quickstart-3", "links": {"self": "/v1/jobs/job_ed7037948e5d4618b3df443892384f32", "cancel": "/v1/jobs/job_ed7037948e5d4618b3df443892384f32/cancel"}}
```

```bash
curl -s http://127.0.0.1:8110/v1/jobs/job_ed7037948e5d4618b3df443892384f32
```

Відповідь (уривок; `result` — той самий `CompletionResult`):

```json
{
  "job_id": "job_ed7037948e5d4618b3df443892384f32",
  "kind": "llm_completion",
  "status": "succeeded",
  "started_at": "2026-10-11T09:57:39.167648Z",
  "finished_at": "2026-10-11T09:57:39.175824Z",
  "result": {
    "completion_id": "cmp_8b0d913bb71a444dab711109689d5b79",
    "valid": true,
    "usage": {"input_tokens": 200, "output_tokens": 6, "cost": {"amount": 0.0, "currency": "USD"}},
    "output_text": "fake:fc3f9368edd97024"
  }
}
```

Повтор `POST` з тим самим ключем повертає той самий job. Стани job — [internals.md](internals.md#стани-job); скасування — `POST /v1/jobs/{job_id}/cancel`.

## Помилки

Помилки — `application/problem+json` за [моделлю помилок](../../../contracts/docs/errors.md). Специфічні для шлюзу:

| HTTP | `code` | Коли | Повторювати |
|---|---|---|---|
| 422 | `validation_failed` | тіло не відповідає контракту; невалідна `output_schema`; модель без `pricing`; валюта бюджету не збігається з ціною; провайдер вимкнено | ні |
| 422 | `limit_exceeded` | оцінка вхідних токенів більша за `max_input_tokens_per_request` або разом з `max_output_tokens` перевищує контекст моделі | ні, зменште дані |
| 404 | `not_found` | псевдонім, провайдер або модель не налаштовано | ні |
| 429 | `budget_exhausted` | застосовний бюджет не вміщує оцінку виклику; `details` — рівень, витрачено, ліміт, `period_resets_at` | після `Retry-After` або збільшення бюджету |
| 429 | `rate_limited` | `max_requests_per_minute` рівня або провайдера | так, після `Retry-After` |
| 502 | `upstream_unavailable` | провайдер не відповів після повторів або відхилив запит | якщо `retryable: true` |
| 422 | `idempotency_key_reused` | ключ уже використано з іншим тілом | ні |
| 409 | `idempotency_in_progress` | запит із цим ключем ще виконується | так |

Невалідний за схемою вихід після всіх спроб — не помилка HTTP: відповідь 200 з `"valid": false`, `validation_errors` і `output_text`.

## Бюджети й облік

Бюджет задається для рівня `platform` (ідентифікатор `platform`), `source` або `task`:

```bash
curl -s -X PUT http://127.0.0.1:8110/v1/budgets/source/demo -H 'Content-Type: application/json' -d '{"scope_type": "source", "scope_id": "demo", "budget": {"amount": 0, "currency": "USD", "period": "day"}}'
```

Відповідь містить `status` з поточним станом лічильника — див. [quickstart.md](quickstart.md#кроки), крок 5. Запит потрапляє під бюджети всіх рівнів зі свого `scope`: `platform` завжди, `source` — якщо задано `scope.source_id`, `task` — якщо `scope.task_id`. Як рахуються вікна, резерв і `period: run` — [internals.md](internals.md#бюджети).

`GET /v1/budgets` повертає всі визначення зі станом; бюджет платформи є завжди (зі сховища або з конфігурації):

```json
{"items": [
  {"scope_type": "platform", "scope_id": "platform", "budget": {"amount": 10.0, "currency": "USD", "period": "day"}, "max_requests_per_minute": 60, "status": {"scope_type": "platform", "scope_id": "platform", "spent": {"amount": 0.0, "currency": "USD"}, "limit": {"amount": 10.0, "currency": "USD", "period": "day"}, "exhausted": false, "resets_at": "2026-10-12T00:00:00Z"}},
  {"scope_type": "source", "scope_id": "demo", "budget": {"amount": 0.0, "currency": "USD", "period": "day"}, "status": {"scope_type": "source", "scope_id": "demo", "spent": {"amount": 0.0, "currency": "USD"}, "limit": {"amount": 0.0, "currency": "USD", "period": "day"}, "exhausted": true, "resets_at": "2026-10-12T00:00:00Z"}}
]}
```

`GET /v1/usage` — облік з фільтрами `scope_type` і `scope_id` (для `source`/`task` обов'язковий), `since`, `until` і групуванням `group_by` = `day` (типово), `model`, `purpose` або `scope`. Тестові виклики (`test_mode`) рахуються окремими рядками. Приклад з `group_by=purpose` після викликів обробника, тест-прогонів і запитів (уривок):

```json
{"items": [
  {"requests": 1, "input_tokens": 462, "output_tokens": 15, "cost": {"amount": 0.0, "currency": "USD"}, "test_mode": false, "purpose": "handler"},
  {"requests": 4, "input_tokens": 1918, "output_tokens": 27, "cost": {"amount": 0.0, "currency": "USD"}, "test_mode": true, "purpose": "handler"},
  {"requests": 2, "input_tokens": 462, "output_tokens": 10, "cost": {"amount": 0.0, "currency": "USD"}, "test_mode": false, "purpose": "other"}
], "totals": {"requests": 7, "input_tokens": 2842, "output_tokens": 52, "cost": {"amount": 0.0, "currency": "USD"}}}
```

## LLM-пакети

Пакет `kind: llm` — маніфест `jane-package.json`, файл інструкцій, опційний шаблон входу й схеми; коду немає. Формат і правило відображення виходу моделі в `HandlerResult` — [довідник пакетів](../../reference/packages/README.md) і розділ «Пакет `llm`: вихід моделі → результат обробника» в [contracts/docs/handler-packages.md](../../../contracts/docs/handler-packages.md).

Шлюз шукає пакет у такому порядку: архів у запиті (`package_archive`) → локальний каталог (`JANE_LLM_PACKAGES_DIR`, типово вбудований `services/llm/packages`) → Registry. Якщо в посиланні є `digest`, він має збігтися з дайджестом знайденого пакета.

Дайджест локального каталогу пакета (канонічний архів):

```powershell
uv run --package jane-llm python -m jane_llm.packages digest services/llm/packages/jane.llm-event-extractor
```

```text
sha256:7dac2065ad9fa06a9830e6d0c4d108518742c63f9937f6a5040275c11340e7f8
```

Публікація каталогу в Registry — `python -m jane_llm.packages publish <каталог> --registry <URL>` (токен — змінна `JANE_LLM_REGISTRY_TOKEN`); у цій документації не перевірялася.

### Виклик пакета

`POST /v1/invocations` за `handler.v1` (дозвіл `handler:invoke`). Ключ ідемпотентності — заголовок `Idempotency-Key` або, якщо його немає, `delivery.delivery_key`. Нижче — виклик вбудованого `jane.llm-event-extractor` на матеріалі з його тесту `concert` після налаштування сценарію з [наступного розділу](#сценарні-відповіді-fake). Файл `invocation.json` (вміст `material` скорочено; повний — `services/llm/packages/jane.llm-event-extractor/tests/concert/material.json`):

```json
{
  "handler": {"package_id": "jane.llm-event-extractor", "version": "1.0.0"},
  "inputs": [{"kind": "material", "material": {"material_id": "tg:-1001234567890:4521", "observation_id": "obs_01J9ZT0C0000000000000004", "source": {"source_id": "news-tg", "kind": "telegram", "name": "City events"}, "fetched_at": "2026-09-27T12:30:00Z", "content": {"kind": "inline", "media_type": "text/plain", "encoding": "utf-8", "data": "Концерт 12 жовтня о 19:00, Філармонія. Вхід вільний."}}}],
  "delivery": {"delivery_key": "demo-concert-1"},
  "context": {"trace": {"source_id": "news-tg"}}
}
```

```bash
curl -s -X POST http://127.0.0.1:8110/v1/invocations -H 'Content-Type: application/json' -H 'Idempotency-Key: demo-concert-1' --data-binary @invocation.json
```

Відповідь — `HandlerResult` (відформатовано):

```json
{
  "invocation_id": "inv_5ec42b721d104c0a8ff383a43c2c7314",
  "handler": {"package_id": "jane.llm-event-extractor", "version": "1.0.0", "digest": "sha256:7dac2065ad9fa06a9830e6d0c4d108518742c63f9937f6a5040275c11340e7f8"},
  "handler_kind": "llm",
  "inputs": [{"kind": "material", "material_id": "tg:-1001234567890:4521", "observation_id": "obs_01J9ZT0C0000000000000004", "content_sha256": "39f16d19ae01f13cceb68b1822579074b18f9bb848a8c4bf5288c088daad8a5d"}],
  "delivery_key": "demo-concert-1",
  "test_mode": false,
  "status": "success",
  "output": {
    "data": {"events": [{"title": "Концерт", "venue": "Філармонія"}]},
    "entities": [
      {
        "entity_type": "event",
        "schema": "jane.llm-event-extractor@1.0.0#event",
        "key": {"scope": "news-tg", "natural": {"message": "tg:-1001234567890:4521"}},
        "fields": {"title": "Концерт", "venue": "Філармонія", "message": "tg:-1001234567890:4521"},
        "observation": {"observation_id": "obs_01J9ZT0C0000000000000004", "observed_at": "2026-09-27T12:30:00Z", "material_id": "tg:-1001234567890:4521", "content_sha256": "39f16d19ae01f13cceb68b1822579074b18f9bb848a8c4bf5288c088daad8a5d"}
      }
    ]
  },
  "started_at": "2026-10-11T09:58:19.727726Z",
  "finished_at": "2026-10-11T09:58:19.760875Z",
  "usage": {"llm": {"provider": "fake", "model": "fake-deterministic-1", "input_tokens": 462, "output_tokens": 15, "cost": {"amount": 0.0, "currency": "USD"}}},
  "diagnostics": {"metrics": {"duration_ms": 33}}
}
```

Повторна доставка з тим самим ключем повертає збережений результат з `"duplicate": true` і заголовком `Idempotency-Replayed: true`, без нового виклику моделі. Виняток — результат `failed` з `failure.kind: budget_exhausted`: він не зберігається, тож повторна доставка після збільшення бюджету виконується заново.

Статуси результату: `success` (є сутності або, якщо пакет не оголошує сутностей, непорожні дані), `empty`, `failed` з `failure.kind` = `schema_mismatch`, `budget_exhausted` або `invalid_params`. Недоступний провайдер чи Registry — не `failed`, а помилка HTTP 502 `upstream_unavailable`. З `"mode": "async"` виклик повертає 202 і job. Збережений результат — `GET /v1/invocations/{invocation_id}`.

### Тест-прогін пакета

`POST /v1/test-runs` (дозвіл `handler:test`) завжди повертає 202 і job; кожен випадок виконується з `test_mode: true`, без запису в робочі дані.

```bash
curl -s -X POST http://127.0.0.1:8110/v1/test-runs -H 'Content-Type: application/json' -H 'Idempotency-Key: quickstart-5' -d '{"handler": {"package_id": "jane.llm-event-extractor", "version": "1.0.0"}}'
```

Підсумок результату job (поля `passed`, `failed` і `name`, `passed`, `actual_status` кожного випадку):

```text
succeeded 2 0
concert True success
prompt-injection-is-data True empty
```

Без сценарію `fake` повертає мінімальну відповідь за схемою (`{"events": []}`), тому випадок `concert` дає `empty` замість `success` і не проходить; випадок `prompt-injection-is-data` проходить в обох конфігураціях.

## Сценарні відповіді fake

Підключення провайдера `fake` може містити сценарії: перший сценарій, умова якого збігається з даними запиту, визначає відповідь. Ключ `responses` дозволено лише з `params.provider: "fake"` — інакше довільний текст сценаріїв не пройде перевірку на секрети.

| Поле сценарію | Зміст |
|---|---|
| `when_data_contains` | підрядок, який має бути в даних |
| `when_data_matches` | регулярний вираз для даних |
| `output` або `output_text` | відповідь JSON або текстом |
| `error` | помилка провайдера; `unavailable` — з можливістю повтору |
| `delay_ms` | затримка відповіді, не більша за `fake.max_delay_ms` |

Затримку для всіх викликів задає `params.delay_ms`. Налаштування, яким виконано приклад виклику пакета:

```json
{
  "connection_id": "fake-scripts",
  "kind": "llm_provider",
  "params": {
    "provider": "fake",
    "responses": [
      {"when_data_contains": "Філармонія", "output": {"events": [{"title": "Концерт", "venue": "Філармонія"}]}}
    ]
  }
}
```

```bash
curl -s -X PUT http://127.0.0.1:8110/v1/connections/fake-scripts -H 'Content-Type: application/json' --data-binary @connection.json
curl -s -X PUT http://127.0.0.1:8110/v1/providers/fake -H 'Content-Type: application/json' -d '{"provider_id": "fake", "kind": "fake", "connection_id": "fake-scripts", "enabled": true, "models": [{"model_id": "fake-deterministic-1", "max_context_tokens": 128000, "supports_structured_output": true, "pricing": {"input_per_mtok": 0, "output_per_mtok": 0, "currency": "USD"}}]}'
```

Перша команда повертає 201 (підключення створено), друга — 200 з визначенням провайдера.

Провайдер `fake` навмисно поводиться як «довірлива» модель: фраза на кшталт `ignore previous instructions … {json}` у каналі інструкцій змінює його відповідь. Тому тест ін'єкції має сенс: та сама фраза всередині даних нічого не змінює, бо шлюз тримає дані в розмежувачах.

## Підключення Anthropic

Не перевірено в цій документації: ключ провайдера під час підготовки не використовувався. Нижче — порядок за кодом `scripts/llm_anthropic.py`, `infra/compose.yaml` і `jane_llm/connections.py`.

Ключ ніколи не передається в API й не зберігається в базі: підключення містить лише посилання `secret_refs.api_key`.

- `file:/run/secrets/anthropic_api_key` — файл у каталозі `JANE_LLM_SECRET_FILES_DIR` (типово `/run/secrets`). У dev-стеку туди монтується git-ignored каталог `.jane/secrets` (або `JANE_SECRETS_DIR`) тільки для читання.
- `env:JANE_SECRET_ANTHROPIC_API_KEY` — змінна середовища сервісу з префіксом `JANE_LLM_SECRET_ENV_PREFIX`.

### Через скрипт у dev-стеку

1. Людина кладе ключ одним рядком у `.jane/secrets/anthropic_api_key` (каталог поза Git).
2. Стек із LLM gateway запущено: `just up llm --project <проєкт>`.
3. Скрипт записує підключення `anthropic-main` → `file:/run/secrets/anthropic_api_key`, провайдер `anthropic` з моделями `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5` і цінами, псевдоніми `default`/`strong` → `claude-opus-5-5`, `cheap` → `claude-haiku-5-5` і бюджет платформи (типово 10 USD на день):

   ```powershell
   uv run --no-project python scripts/llm_anthropic.py --project <проєкт> --check
   ```

   `--check` робить один короткий запит через псевдонім `cheap`; `--budget-usd-per-day` змінює бюджет платформи.

### Вручну через API

1. `PUT /v1/connections/anthropic-main` з `kind: llm_provider`, `params.api_base: https://api.anthropic.com` і `secret_refs.api_key`.
2. `POST /v1/connections/anthropic-main/test` — перевіряє, чи розв'язується посилання в середовищі сервісу (без звернення до провайдера). Відповідь для `env:JANE_SECRET_ANTHROPIC_API_KEY` без змінної:

   ```json
   {"ok": false, "checked_at": "2026-10-11T09:58:34Z", "latency_ms": 0, "secrets_resolved": {"api_key": false}, "message": "secret reference(s) not resolvable in this service's environment: ['api_key']"}
   ```

3. `PUT /v1/providers/anthropic` з `kind: anthropic`, `connection_id` і моделями з `pricing`.
4. `PUT /v1/model-aliases/<псевдонім>` для потрібних псевдонімів.

Те саме можна задати seed-файлом — [configuration.md](configuration.md#seed-файл).

Структурований вихід: якщо модель позначено `supports_structured_output` і схему можна виразити підмножиною JSON Schema Messages API, адаптер передає її як `output_config.format`; інакше схема додається до системних інструкцій. Відповідь шлюз перевіряє за повною схемою в будь-якому разі.

## Композиція в Jane

Місце шлюзу серед модулів показано на [схемі складу платформи](../../../README.md#як-складається-платформа).

- **Orchestrator** викликає шлюз як виконавця етапів `kind: llm` (у `infra/compose.local.example.yaml`: роль `llm`, `handler_kinds: ["llm"]`). Він передає `context.trace` з `source_id`, `task_id`, `run_id` — за ними шлюз застосовує бюджети рівнів — і переносить `limits.llm` джерел і завдань у бюджети шлюзу (`PUT`/`DELETE /v1/budgets/...`, дозвіл `llm:admin`).
- **Assistant** робить структуровані запити з `scope.purpose` (`onboarding`, `improvement`, `unknown_material`), `scope.run_id` свого запуску й бюджетом запуску в `limits.llm.budget`. Він використовує псевдоніми `cheap` і `strong` — їх треба створити в шлюзі (`PUT /v1/model-aliases/...`), інакше запити Assistant отримують 404. Деталі — [Assistant](../assistant/integration.md).
- **Admin UI** показує й змінює провайдерів, псевдоніми, бюджети, облік і підключення.
- У dev-стеку (`infra/compose.yaml`) шлюз приймає ключі `admin`, `orchestrator` (`handler:invoke`, `connections:write`, `llm:admin`) і `assistant` (`llm:invoke`).

## Заміна сумісною реалізацією

Сумісна реалізація має відповідати контрактам `contracts/openapi/llm.v1.yaml` і, для етапів `kind: llm`, `contracts/openapi/handler.v1.yaml` (разом із `common.yaml`): ідемпотентність за `Idempotency-Key`, job за `202`, модель помилок, зокрема 429 `budget_exhausted` без звернення до провайдера.

Мінімум для окремих клієнтів:

| Клієнт | Потрібні операції |
|---|---|
| Assistant | `POST /v1/completions`, для `mode: async` — `GET /v1/jobs/{job_id}` |
| Orchestrator | `handler.v1` (`/v1/invocations`, `/v1/test-runs`, `/v1/connections`), `PUT`/`DELETE /v1/budgets/...` |
| Admin UI | увесь `llm.v1` і `/v1/connections` |

Відповідність перевіряють контрактні тести сервісу (`services/llm/tests/test_contract.py`, входять у `just test llm`). Новий провайдер у межах цієї реалізації — клас з протоколом `ProviderAdapter` (`jane_llm/providers/base.py`), зареєстрований у `ADAPTERS` (`jane_llm/providers/__init__.py`); це зміна коду сервісу.
