# listImprovementRuns

Запуски вдосконалення (job `kind = improvement`), новіші першими

Контракт: [contracts/openapi/assistant.v1.yaml](../../../../../../contracts/openapi/assistant.v1.yaml).

```http
GET /v1/improvement-runs
```

## Опис із контракту

```text
Job, створені `startImprovement`, з `result` = `ImprovementResult` для завершених — щоб адмінка відновила
список після перезавантаження. Курсорна пагінація (`limit`, `cursor` → `next_cursor`); порядок —
`created_at` спадно, за рівності — `job_id` спадно. Фільтри — за мітками job (`labels.package_id`,
`labels.source_id`, `labels.problem_group_id`) і станом. Завершені job зберігаються
`limits.transfer.job_retention_seconds` асистента.
```

## Доступ

```json
{
  "scope": "assistant:use",
  "security": [
    {
      "bearerAuth": []
    }
  ]
}
```

## Параметри

| Ім’я | Розміщення | Обов’язковий |
|---|---|---|
| `cursor` | `query` | ні |
| `limit` | `query` | ні |
| `package_id` | `query` | ні |
| `source_id` | `query` | ні |
| `problem_group_id` | `query` | ні |
| `status` | `query` | ні |

```json
[
  {
    "description": "Непрозорий курсор з `next_cursor` попередньої сторінки.",
    "in": "query",
    "name": "cursor",
    "required": false,
    "schema": {
      "maxLength": 2048,
      "type": "string"
    }
  },
  {
    "description": "Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму.",
    "in": "query",
    "name": "limit",
    "required": false,
    "schema": {
      "default": 50,
      "minimum": 1,
      "type": "integer"
    }
  },
  {
    "in": "query",
    "name": "package_id",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "source_id",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "problem_group_id",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "description": "Лише job у цих станах (параметр можна повторити).",
    "explode": true,
    "in": "query",
    "name": "status",
    "required": false,
    "schema": {
      "items": {
        "$ref": "../schemas/common/job.schema.json#/$defs/JobStatus"
      },
      "type": "array"
    },
    "style": "form"
  }
]
```

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Сторінка job вдосконалення. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "page": {
            "value": {
              "items": [
                {
                  "created_at": "2026-09-27T10:00:00Z",
                  "finished_at": "2026-09-27T10:01:30Z",
                  "job_id": "job_01J9ZW00000000000000IMPROV",
                  "kind": "improvement",
                  "labels": {
                    "package_id": "shop-example.product-extractor",
                    "problem_group_id": "pg_01J9ZW0000000000000000001",
                    "source_id": "shop-example"
                  },
                  "links": {
                    "cancel": "/v1/jobs/job_01J9ZW00000000000000IMPROV/cancel",
                    "self": "/v1/jobs/job_01J9ZW00000000000000IMPROV"
                  },
                  "result": {
                    "activated": false,
                    "attempts": 1,
                    "outcome": "new_version",
                    "version": {
                      "package_id": "shop-example.product-extractor",
                      "version": "1.2.1"
                    }
                  },
                  "status": "succeeded"
                }
              ],
              "next_cursor": null
            }
          }
        },
        "schema": {
          "$ref": "common.yaml#/components/schemas/JobList"
        }
      }
    },
    "description": "Сторінка job вдосконалення."
  },
  "401": {
    "content": {
      "application/problem+json": {
        "examples": {
          "unauthenticated": {
            "value": {
              "code": "unauthenticated",
              "status": 401,
              "title": "Unauthenticated",
              "type": "urn:jane:problem:unauthenticated"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Немає або недійсний токен (`unauthenticated`)."
  },
  "422": {
    "content": {
      "application/problem+json": {
        "examples": {
          "idempotencyReused": {
            "$ref": "#/components/examples/ProblemIdempotencyReused"
          },
          "validation": {
            "$ref": "#/components/examples/ProblemValidation"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо)."
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-scope": "assistant:use"
}
```

## Схеми

- [contracts/schemas/common/job.schema.json#/$defs/JobStatus](../../../../../../contracts/schemas/common/job.schema.json#/$defs/JobStatus)
- [contracts/openapi/common.yaml#/components/schemas/JobList](../../../../../../contracts/openapi/common.yaml#/components/schemas/JobList)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
