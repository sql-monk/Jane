# GET /v1/jobs/{job_id}

> Згенеровано `scripts/docs_reference.py` з [assistant.v1.yaml](../../../../../contracts/openapi/assistant.v1.yaml#L481). Не редагуйте вручну.

**Стан, прогрес і результат тривалої операції**

| Властивість | Значення |
|---|---|
| operationId | `getJob` |
| Метод і шлях | `GET /v1/jobs/{job_id}` |
| Scope | `assistant:use` |
| Ідемпотентність | — |
| Теги | jobs |

`Job.result` завершеного (`succeeded`) job за `kind`: `onboarding` — `OnboardingSession`; `onboarding_acceptance` — `AcceptanceResult`; `improvement` — `ImprovementResult`; `unknown_material` — `UnknownMaterialResult`. Job сесії підключення мають `labels.session_id` і `links.session`.

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `job_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Поточний стан job. | `job` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

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

Приклад `running`:

```json
{
  "job_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
  "kind": "collection",
  "status": "running",
  "created_at": "2026-09-27T10:00:00Z",
  "started_at": "2026-09-27T10:00:01Z",
  "updated_at": "2026-09-27T10:02:00Z",
  "progress": {
    "completed": 120,
    "total": null,
    "unit": "pages",
    "counters": {
      "fetched": 120,
      "skipped_robots": 3,
      "skipped_out_of_scope": 41,
      "duplicates": 17
    },
    "updated_at": "2026-09-27T10:02:00Z"
  },
  "links": {
    "self": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
    "cancel": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F/cancel"
  }
}
```

Приклад `failed`:

```json
{
  "job_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
  "kind": "collection",
  "status": "failed",
  "created_at": "2026-09-27T10:00:00Z",
  "started_at": "2026-09-27T10:00:01Z",
  "finished_at": "2026-09-27T10:00:09Z",
  "error": {
    "type": "urn:jane:problem:source_unavailable",
    "title": "Source unavailable",
    "status": 502,
    "code": "source_unavailable",
    "retryable": true,
    "detail": "https://shop.example.test/ returned HTTP 503 for 5 consecutive attempts"
  }
}
```

Приклад `onboardingSucceeded`:

```json
{
  "job_id": "job_01J9ZY0000000000000000JOB",
  "kind": "onboarding",
  "status": "succeeded",
  "created_at": "2026-09-27T09:00:00Z",
  "started_at": "2026-09-27T09:00:00Z",
  "finished_at": "2026-09-27T09:00:02Z",
  "labels": {
    "session_id": "onb_01J9ZY0000000000000000001"
  },
  "links": {
    "self": "/v1/jobs/job_01J9ZY0000000000000000JOB",
    "cancel": "/v1/jobs/job_01J9ZY0000000000000000JOB/cancel",
    "session": "/v1/onboarding-sessions/onb_01J9ZY0000000000000000001"
  },
  "result": {
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
}
```

Приклад `acceptanceSucceeded`:

```json
{
  "job_id": "job_01J9ZY00000000000000ACCEPT",
  "kind": "onboarding_acceptance",
  "status": "succeeded",
  "created_at": "2026-09-27T09:20:00Z",
  "started_at": "2026-09-27T09:20:00Z",
  "finished_at": "2026-09-27T09:20:09Z",
  "idempotency_key": "accept-shop-1",
  "labels": {
    "session_id": "onb_01J9ZY0000000000000000001"
  },
  "links": {
    "self": "/v1/jobs/job_01J9ZY00000000000000ACCEPT",
    "cancel": "/v1/jobs/job_01J9ZY00000000000000ACCEPT/cancel",
    "session": "/v1/onboarding-sessions/onb_01J9ZY0000000000000000001"
  },
  "result": {
    "collector_rules": {
      "package_id": "shop-example.rules",
      "version": "1.0.0",
      "digest": "sha256:2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881"
    },
    "extractors": [
      {
        "action": "bind_existing",
        "package": {
          "package_id": "shop-example.product-extractor",
          "version": "1.2.0"
        },
        "test_report": {
          "package": {
            "package_id": "shop-example.product-extractor",
            "version": "1.2.0"
          },
          "passed": 2,
          "failed": 0,
          "cases": [
            {
              "name": "product-a100",
              "passed": true,
              "expected_status": "success",
              "actual_status": "success"
            },
            {
              "name": "category-page-empty",
              "passed": true,
              "expected_status": "empty",
              "actual_status": "empty"
            }
          ]
        }
      }
    ],
    "source_draft": {
      "source_id": "shop-example",
      "kind": "web",
      "title": "Shop Example",
      "locator": {
        "url": "https://shop.example.test/"
      },
      "expected_entity_types": [
        "product"
      ]
    },
    "activated": false
  }
}
```

Приклад `improvementSucceeded`:

```json
{
  "job_id": "job_01J9ZW00000000000000IMPROV",
  "kind": "improvement",
  "status": "succeeded",
  "created_at": "2026-09-27T10:00:00Z",
  "started_at": "2026-09-27T10:00:00Z",
  "finished_at": "2026-09-27T10:01:30Z",
  "idempotency_key": "improve-pg-1",
  "progress": {
    "completed": 4,
    "total": 4,
    "unit": "steps",
    "message": "published shop-example.product-extractor@1.2.1"
  },
  "labels": {
    "package_id": "shop-example.product-extractor",
    "source_id": "shop-example",
    "problem_group_id": "pg_01J9ZW0000000000000000001"
  },
  "links": {
    "self": "/v1/jobs/job_01J9ZW00000000000000IMPROV",
    "cancel": "/v1/jobs/job_01J9ZW00000000000000IMPROV/cancel"
  },
  "result": {
    "outcome": "new_version",
    "version": {
      "package_id": "shop-example.product-extractor",
      "version": "1.2.1",
      "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
    },
    "attempts": 1,
    "test_reports": [
      {
        "context": "tests",
        "report": {
          "package": {
            "package_id": "shop-example.product-extractor",
            "version": "1.2.1"
          },
          "passed": 3,
          "failed": 0,
          "cases": [
            {
              "name": "product-a100",
              "passed": true,
              "expected_status": "success",
              "actual_status": "success"
            },
            {
              "name": "category-page-empty",
              "passed": true,
              "expected_status": "empty",
              "actual_status": "empty"
            },
            {
              "name": "problem-p1",
              "passed": true,
              "expected_status": "success",
              "actual_status": "success"
            }
          ]
        }
      }
    ],
    "activated": false,
    "costs": {
      "amount": 0.12,
      "currency": "USD"
    }
  }
}
```

Приклад `improvementProposalOnly`:

```json
{
  "job_id": "job_01J9ZW0000000000000PROPOS",
  "kind": "improvement",
  "status": "succeeded",
  "created_at": "2026-09-27T10:00:00Z",
  "started_at": "2026-09-27T10:00:00Z",
  "finished_at": "2026-09-27T10:01:10Z",
  "labels": {
    "package_id": "shop-example.product-extractor"
  },
  "links": {
    "self": "/v1/jobs/job_01J9ZW0000000000000PROPOS",
    "cancel": "/v1/jobs/job_01J9ZW0000000000000PROPOS/cancel"
  },
  "result": {
    "outcome": "proposal_only",
    "version": {
      "package_id": "shop-example.product-extractor",
      "version": "1.2.1"
    },
    "attempts": 1,
    "activated": false,
    "costs": {
      "amount": 0.08,
      "currency": "USD"
    },
    "proposal": {
      "based_on": {
        "package_id": "shop-example.product-extractor",
        "version": "1.2.0"
      },
      "version": "1.2.1",
      "schema_change": "none",
      "change_summary": "Support the .price-new selector.",
      "manifest": {
        "schema_version": "1",
        "package_id": "shop-example.product-extractor",
        "version": "1.2.1",
        "kind": "extractor",
        "title": "Shop Example product cards",
        "entry": {
          "runtime": "python",
          "module": "product_extractor.main",
          "callable": "extract"
        },
        "input": {
          "accepts": [
            "material"
          ],
          "media_types": [
            "text/html"
          ]
        },
        "output": {
          "entities": [
            {
              "entity_type": "product",
              "schema": "schemas/product.schema.json",
              "key_fields": [
                "sku"
              ]
            }
          ]
        },
        "dependencies": {
          "runtime_profile": "python-extractor@1",
          "python": []
        },
        "access": {
          "network": "none"
        },
        "tests": [
          {
            "name": "problem-p1",
            "input": {
              "material": "tests/problem-p1/material.json"
            },
            "expected_status": "success",
            "expected": "tests/problem-p1/expected.json",
            "compare": "subset",
            "origin": "problem_sample"
          }
        ],
        "provenance": {
          "created_by": "llm",
          "based_on": {
            "package_id": "shop-example.product-extractor",
            "version": "1.2.0"
          },
          "change_summary": "Support the .price-new selector.",
          "llm": {
            "reason": "improvement",
            "assistant_job_id": "job_01J9ZW0000000000000PROPOS"
          }
        }
      },
      "files": {
        "src/product_extractor/main.py": {
          "encoding": "utf-8",
          "data": "import re\n\n_PRICE = re.compile(r'class=\"price(?:-new)?\"[^>]*>([0-9.]+)')\n"
        },
        "tests/problem-p1/expected.json": {
          "encoding": "utf-8",
          "data": "{\"entities\": [{\"entity_type\": \"product\", \"fields\": {\"sku\": \"C-300\"}}]}"
        }
      },
      "omitted_files": [
        "tests/problem-p1/material.json"
      ],
      "diff": "--- a/src/product_extractor/main.py\n+++ b/src/product_extractor/main.py\n@@ -1,3 +1,3 @@\n import re\n\n-_PRICE = re.compile(r'class=\"price\"[^>]*>([0-9.]+)')\n+_PRICE = re.compile(r'class=\"price(?:-new)?\"[^>]*>([0-9.]+)')\n"
    }
  }
}
```

Приклад `unknownSucceeded`:

```json
{
  "job_id": "job_01J9ZQ5A00000000000UNKNOWN",
  "kind": "unknown_material",
  "status": "succeeded",
  "created_at": "2026-09-27T10:05:01Z",
  "started_at": "2026-09-27T10:05:01Z",
  "finished_at": "2026-09-27T10:05:03Z",
  "labels": {
    "source_id": "shop-example"
  },
  "links": {
    "self": "/v1/jobs/job_01J9ZQ5A00000000000UNKNOWN",
    "cancel": "/v1/jobs/job_01J9ZQ5A00000000000UNKNOWN/cancel"
  },
  "result": {
    "classification": {
      "material_type": "gift_card_listing",
      "confidence": 0.82
    },
    "suggestion": {
      "action": "new_extractor",
      "details": "no extractor handles gift_card_listing materials carrying product"
    }
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
