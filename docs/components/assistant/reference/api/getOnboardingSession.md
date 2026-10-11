# GET /v1/onboarding-sessions/{session_id}

> Згенеровано `scripts/docs_reference.py` з [assistant.v1.yaml](../../../../../contracts/openapi/assistant.v1.yaml#L161). Не редагуйте вручну.

**Стан підключення — кандидати, вибірка, аналіз, варіанти**

| Властивість | Значення |
|---|---|
| operationId | `getOnboardingSession` |
| Метод і шлях | `GET /v1/onboarding-sessions/{session_id}` |
| Scope | `assistant:use` |
| Ідемпотентність | — |
| Теги | onboarding |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `session_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сесія. | `OnboardingSession` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `session_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `status` | enum: `resolving`, `needs_disambiguation`, `sampling`, `analyzing`, `proposals_ready`, `insufficient_sample`, `applying`, `completed`, `failed`, `cancelled` | так |  |
| `query` | `string` | так |  |
| `candidates` | array of `SourceCandidate` | ні |  |
| `candidates[].candidate_id` | `string` | так |  |
| `candidates[].title` | `string` | так |  |
| `candidates[].url` | `string` (uri) | ні |  |
| `candidates[].telegram_username` | `string` | ні |  |
| `candidates[].description` | `string` | ні |  |
| `candidates[].confidence` | `number` | ні | мін. `0`; макс. `1` |
| `selected_candidate_id` | `string` | ні |  |
| `sample` | `object` | ні |  |
| `sample.materials` | `integer` | ні |  |
| `sample.distinct_types` | `integer` | ні |  |
| `sample.confidence` | `number` | ні |  |
| `sample.sufficient` | `boolean` | ні |  |
| `sample.message` | `string` | ні |  |
| `analysis` | `SourceAnalysis` | ні |  |
| `analysis.source_kind` | `string` | ні |  |
| `analysis.discovery_methods` | array of `string` | ні | Доступні способи обходу (sitemap, feed, listing, api_feed, recursive…). |
| `analysis.material_types` | array of `object` | ні |  |
| `analysis.material_types[].type` | `string` | так |  |
| `analysis.material_types[].count` | `integer` | так |  |
| `analysis.material_types[].example_urls` | array of `string` | ні |  |
| `analysis.entities` | array of `object` | ні |  |
| `analysis.entities[].entity_type` | `string` | так |  |
| `analysis.entities[].fields` | array of `FieldInfo` | так |  |
| `proposals` | array of `Proposal` | ні |  |
| `proposals[].proposal_id` | `string` | так |  |
| `proposals[].title` | `string` | так |  |
| `proposals[].summary` | `string` | ні |  |
| `proposals[].recommended` | `boolean` | ні |  |
| `proposals[].collector_rules` | `WebRules` \| `TelegramRules` | так | Правила колектора (ТЗ §6, §13.1 п.1): версіонуються як пакет kind=collector-rules або передаються колектору inline/з локального файла в автономному режимі. Web: комбінація стратегій пошуку в спільних межах обходу; Telegram: канали, історія, редагування. Числові обмеження — лише через limits (успадкування platform → source → task). |
| `proposals[].extractors` | array of `ExtractorPlan` | так |  |
| `proposals[].extractors[].entity_type` | `string` | так |  |
| `proposals[].extractors[].action` | enum: `bind_existing`, `fork`, `create` | так |  |
| `proposals[].extractors[].package` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `proposals[].extractors[].match_score` | `number` | ні | мін. `0`; макс. `1` |
| `proposals[].extractors[].tested_on_samples` | `object` | ні |  |
| `proposals[].coverage` | `object` | ні |  |
| `proposals[].coverage.estimated_materials` | `integer` | ні |  |
| `proposals[].coverage.entity_types` | array of `string` | ні |  |
| `proposals[].coverage.notes` | `string` | ні |  |
| `proposals[].cost` | `object` | ні |  |
| `proposals[].cost.requests_per_run_estimate` | `integer` | ні |  |
| `proposals[].cost.llm_setup_cost` | `Money` | ні |  |
| `proposals[].cost.llm_cost_per_run` | `Money` | ні |  |
| `proposals[].risks` | array of `string` | ні |  |
| `costs` | `Money` | ні |  |
| `costs.amount` | `number` | так | мін. `0` |
| `costs.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `job_id` | `string` | ні |  |
| `created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `error` | `problem` | ні | Єдина модель помилки всіх API Jane: RFC 9457 (application/problem+json) з розширеннями 'code', 'retryable', 'errors', 'trace_id'. Клієнт приймає рішення за 'code' (стабільний машинний код), а не за 'title'/'detail'. Невідомий 'code' обробляється за HTTP-статусом і 'retryable'. |
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

Приклад `ambiguous`:

```json
{
  "session_id": "onb_01J9ZY0000000000000000001",
  "status": "needs_disambiguation",
  "query": "Shop Example kettles",
  "candidates": [
    {
      "candidate_id": "cand_1",
      "title": "Shop Example",
      "url": "https://shop.example.test/",
      "confidence": 0.62
    },
    {
      "candidate_id": "cand_2",
      "title": "Shop Example Outlet",
      "url": "https://outlet.shop.example.test/",
      "confidence": 0.35
    }
  ],
  "job_id": "job_01J9ZY0000000000000000JOB",
  "created_at": "2026-09-27T09:00:00Z"
}
```

Приклад `proposals`:

```json
{
  "session_id": "onb_01J9ZY0000000000000000001",
  "status": "proposals_ready",
  "query": "Shop Example kettles",
  "selected_candidate_id": "cand_1",
  "sample": {
    "materials": 38,
    "distinct_types": 4,
    "confidence": 0.86,
    "sufficient": true
  },
  "analysis": {
    "source_kind": "web",
    "discovery_methods": [
      "sitemap",
      "listing",
      "recursive"
    ],
    "material_types": [
      {
        "type": "product",
        "count": 24,
        "example_urls": [
          "https://shop.example.test/product/a-100"
        ]
      },
      {
        "type": "category",
        "count": 9
      }
    ],
    "entities": [
      {
        "entity_type": "product",
        "fields": [
          {
            "name": "sku",
            "type": "string",
            "coverage": 1
          },
          {
            "name": "price",
            "type": "money",
            "coverage": 0.96
          }
        ]
      }
    ]
  },
  "proposals": [
    {
      "proposal_id": "p1",
      "title": "Sitemap + product extractor",
      "summary": "Повний каталог через sitemap; наявний екстрактор з репозиторію.",
      "recommended": true,
      "collector_rules": {
        "collector": "web",
        "scope": {
          "allowed_domains": [
            "shop.example.test"
          ]
        },
        "strategies": [
          {
            "type": "sitemap"
          }
        ]
      },
      "extractors": [
        {
          "entity_type": "product",
          "action": "bind_existing",
          "package": {
            "package_id": "shop-example.product-extractor",
            "version": "1.2.0"
          },
          "match_score": 0.93,
          "tested_on_samples": {
            "passed": 23,
            "failed": 1
          }
        }
      ],
      "coverage": {
        "estimated_materials": 18000,
        "entity_types": [
          "product"
        ]
      },
      "cost": {
        "requests_per_run_estimate": 18500,
        "llm_setup_cost": {
          "amount": 0.31,
          "currency": "USD"
        },
        "llm_cost_per_run": {
          "amount": 0,
          "currency": "USD"
        }
      },
      "risks": [
        "sitemap may omit discontinued products"
      ]
    }
  ],
  "costs": {
    "amount": 0.31,
    "currency": "USD"
  },
  "job_id": "job_01J9ZY0000000000000000JOB",
  "created_at": "2026-09-27T09:00:00Z"
}
```

Приклад `insufficient`:

```json
{
  "session_id": "onb_01J9ZY0000000000000000002",
  "status": "insufficient_sample",
  "query": "https://tiny.example.test/",
  "sample": {
    "materials": 4,
    "distinct_types": 1,
    "confidence": 0.3,
    "sufficient": false,
    "message": "site has only 4 reachable pages; cannot distinguish material types"
  },
  "costs": {
    "amount": 0.05,
    "currency": "USD"
  },
  "created_at": "2026-09-27T09:00:00Z"
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
