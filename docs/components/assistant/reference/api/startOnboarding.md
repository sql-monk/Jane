# POST /v1/onboarding-sessions

> Згенеровано `scripts/docs_reference.py` з [assistant.v1.yaml](../../../../../contracts/openapi/assistant.v1.yaml#L97). Не редагуйте вручну.

**Почати підключення джерела (назва сайту/каналу або точне посилання)**

| Властивість | Значення |
|---|---|
| operationId | `startOnboarding` |
| Метод і шлях | `POST /v1/onboarding-sessions` |
| Scope | `assistant:use` |
| Ідемпотентність | обов'язковий `Idempotency-Key` |
| Теги | onboarding |

202 + Job (`kind: onboarding`). Ідентифікатор створеної сесії — `Job.labels.session_id`, її адреса — `Job.links.session` (`/v1/onboarding-sessions/{session_id}`); ті самі поля мають усі job сесії (продовження після `selectCandidate`, `acceptProposal`). `Job.result` завершеного job — `OnboardingSession` на момент завершення (зокрема `needs_disambiguation`, `proposals_ready`, `insufficient_sample`).

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `Idempotency-Key` | header | `string` | так | Ключ ідемпотентності (1–255 друкованих ASCII-символів; рекомендовано UUID або детермінований ключ доставки). Повтор із тим самим ключем і тим самим тілом повертає збережену відповідь (заголовок `Idempotency-Replayed: true`) без повторного ефекту. Той самий ключ з іншим тілом — 422 `idempotency_key_reused`. Запит ще виконується — 409 `idempotency_in_progress` (retryable). Сервіс пам'ятає ключ щонайменше `limits.transfer.idempotency_ttl_seconds`. |

## Тіло запиту

Тип вмісту `application/json`, схема `OnboardingRequest`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `query` | `string` | так | Назва сайту чи каналу або точне посилання.; мін. довжина `1`; макс. довжина `2000` |
| `source_kind` | `string` | ні | Тип джерела. Розширюється додаванням нових значень (клієнти мають терпіти невідомі значення).; шаблон `"^[a-z][a-z0-9_-]{1,31}$"` |
| `expected_entity_types` | array of `string` | ні |  |
| `crawl_hints` | `object` | ні | Часткові правила обходу від користувача (фрагмент CollectorRules), які асистент має врахувати. |
| `limits` | `llm` | ні |  |
| `limits.max_requests_per_minute` | `integer` | ні | мін. `1` |
| `limits.max_input_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.max_output_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `limits.budget.amount` | `number` | так | мін. `0` |
| `limits.budget.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `limits.budget.period` | enum: `run`, `day`, `week`, `month`, `total` | так |  |
| `limits.max_improvement_attempts` | `integer` | ні | Скільки спроб вдосконалення екстрактора на одну групу проблем.; мін. `0` |
| `limits.max_onboarding_samples` | `integer` | ні | Верхня межа вибірки під час дослідження джерела (фактична кількість адаптивна).; мін. `1` |
| `limits.min_onboarding_confidence` | `number` | ні | Поріг достатньої впевненості вибірки під час дослідження джерела (ТЗ §8): асистент вибирає матеріали, доки оцінка впевненості не досягне порога; не досягнуто в межах бюджету й max_onboarding_samples — сесія insufficient_sample. Вищий поріг — більша вибірка й витрати, тому hard_caps обмежують його зверху. Типово 0.8.; макс. `1` |
| `auto_activation` | `boolean` | ні | типово `false` |

Приклад `byName`:

```json
{
  "query": "Shop Example kettles",
  "expected_entity_types": [
    "product"
  ],
  "limits": {
    "budget": {
      "amount": 2,
      "currency": "USD",
      "period": "total"
    },
    "max_onboarding_samples": 60
  },
  "auto_activation": false
}
```

Приклад `byUrl`:

```json
{
  "query": "https://news.example.test/",
  "source_kind": "web",
  "expected_entity_types": [
    "event"
  ],
  "crawl_hints": {
    "scope": {
      "allowed_domains": [
        "news.example.test"
      ]
    }
  }
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `202` | Підключення почато; `labels.session_id` і `links.session` — сесія. | `job` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |
| `429` | Перевищено частоту (`rate_limited`) або бюджет (`budget_exhausted`). | `problem` |

### Відповідь 202

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `job_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `kind` | `string` | так | Вид операції в межах сервісу, наприклад 'collection', 'invocation', 'test_run', 'run', 'onboarding', 'improvement', 'upstream_port'.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `status` | enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | так |  |
| `created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `started_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `finished_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `progress` | `JobProgress` | ні |  |
| `progress.completed` | `integer` | ні | мін. `0` |
| `progress.total` | `integer \| null` | ні | Відома загальна кількість одиниць; null — невідома (наприклад під час рекурсивного обходу).; мін. `0` |
| `progress.unit` | `string` | ні |  |
| `progress.message` | `string` | ні |  |
| `progress.counters` | `object` | ні | Довільні лічильники, наприклад {"fetched": 10, "skipped_robots": 2}. |
| `progress.updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `result` | `object` | ні | Результат, коли status = succeeded. Форма залежить від 'kind' і описана в API відповідної операції. Великий результат передається як result_ref. |
| `result_ref` | `InlineContent` \| `BlobContent` | ні | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `error` | `problem` | ні | Причина, коли status = failed. Для cancelled причина — у cancellation. |
| `error.type` | `string` (uri-reference) | так | URI типу проблеми: 'urn:jane:problem:&lt;code>'. |
| `error.title` | `string` | так | Короткий людський опис типу проблеми. |
| `error.status` | `integer` | так | мін. `400`; макс. `599` |
| `error.detail` | `string` | ні | Пояснення конкретного випадку. Без секретів і без вмісту матеріалів. |
| `error.instance` | `string` (uri-reference) | ні |  |
| `error.code` | `string` | так | Стабільний машинний код у snake_case. Відомі коди — $defs/KnownErrorCode. Сервіс може додати власний код лише разом з оновленням каталогу в contracts/.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `error.retryable` | `boolean` | ні | true — ту саму операцію (з тим самим Idempotency-Key) можна безпечно повторити пізніше. |
| `error.retry_after_seconds` | `integer` | ні | Дублює заголовок Retry-After для клієнтів, які читають лише тіло.; мін. `0` |
| `error.errors` | array of `FieldError` | ні | Помилки окремих полів або параметрів (для validation_failed). |
| `error.errors[].pointer` | `string` | ні | JSON Pointer (RFC 6901) до поля тіла запиту, наприклад '/stages/2/handler/version'. |
| `error.errors[].parameter` | `string` | ні | Ім'я query/path/header параметра. |
| `error.errors[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `error.errors[].message` | `string` | так |  |
| `error.trace_id` | `string` | ні |  |
| `error.details` | `object` | ні | Додаткові структуровані дані, специфічні для коду (наприклад 'limit', 'actual' для limit_exceeded). |
| `cancellation` | `JobCancellation` | ні |  |
| `cancellation.requested_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `cancellation.requested_by` | `string` | ні |  |
| `cancellation.reason` | `string` | ні | макс. довжина `1000` |
| `idempotency_key` | `string` | ні | макс. довжина `255` |
| `links` | `object` | ні | Пов'язані ресурси: self, cancel, result, run, collection тощо. |
| `labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |

Приклад `queued`:

```json
{
  "job_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
  "kind": "collection",
  "status": "queued",
  "created_at": "2026-09-27T10:00:00Z",
  "links": {
    "self": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
    "cancel": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F/cancel"
  }
}
```

Приклад `onboarding`:

```json
{
  "job_id": "job_01J9ZY0000000000000000JOB",
  "kind": "onboarding",
  "status": "queued",
  "created_at": "2026-09-27T09:00:00Z",
  "idempotency_key": "onboard-shop-1",
  "labels": {
    "session_id": "onb_01J9ZY0000000000000000001"
  },
  "links": {
    "self": "/v1/jobs/job_01J9ZY0000000000000000JOB",
    "cancel": "/v1/jobs/job_01J9ZY0000000000000000JOB/cancel",
    "session": "/v1/onboarding-sessions/onb_01J9ZY0000000000000000001"
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `422`, `429`.
- Операція асинхронна: `202` повертає job; стан, прогрес і результат — через `GET /v1/jobs/{job_id}`.
