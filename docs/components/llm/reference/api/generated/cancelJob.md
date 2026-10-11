# cancelJob

Запит на скасування job (ідемпотентний)

Контракт: [contracts/openapi/llm.v1.yaml](../../../../../../contracts/openapi/llm.v1.yaml).

```http
POST /v1/jobs/{job_id}/cancel
```

## Опис із контракту

```text
202 — скасування прийнято, job переходить у `cancelling`, далі в `cancelled`.
200 — job уже в термінальному стані; повертається як є, без змін.
Повторний виклик безпечний, тому Idempotency-Key не потрібен.
```

## Доступ

```json
{
  "scope": [
    "llm:admin",
    "llm:invoke"
  ],
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
| `job_id` | `path` | так |

```json
[
  {
    "in": "path",
    "name": "job_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Id"
    }
  }
]
```

## Тіло запиту

```json
{
  "content": {
    "application/json": {
      "examples": {
        "reason": {
          "value": {
            "reason": "wrong scope"
          }
        }
      },
      "schema": {
        "$ref": "common.yaml#/components/schemas/JobCancelRequest"
      }
    }
  },
  "required": false
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Job уже завершено; стан не змінено. | ні |
| `202` | Скасування прийнято. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "failed": {
            "$ref": "common.yaml#/components/examples/JobFailed"
          }
        },
        "schema": {
          "$ref": "common.yaml#/components/schemas/Job"
        }
      }
    },
    "description": "Job уже завершено; стан не змінено."
  },
  "202": {
    "content": {
      "application/json": {
        "examples": {
          "cancelling": {
            "$ref": "common.yaml#/components/examples/JobCancelling"
          }
        },
        "schema": {
          "$ref": "common.yaml#/components/schemas/Job"
        }
      }
    },
    "description": "Скасування прийнято."
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
  "404": {
    "content": {
      "application/problem+json": {
        "examples": {
          "notFound": {
            "$ref": "#/components/examples/ProblemNotFound"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Ресурс не знайдено (`not_found`)."
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-no-idempotency-key": "cancellation is idempotent by nature",
  "x-jane-scope": [
    "llm:admin",
    "llm:invoke"
  ]
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Id](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Id)
- [contracts/openapi/common.yaml#/components/schemas/JobCancelRequest](../../../../../../contracts/openapi/common.yaml#/components/schemas/JobCancelRequest)
- [contracts/openapi/common.yaml#/components/schemas/Job](../../../../../../contracts/openapi/common.yaml#/components/schemas/Job)
- [contracts/openapi/common.yaml#/components/examples/JobFailed](../../../../../../contracts/openapi/common.yaml#/components/examples/JobFailed)
- [contracts/openapi/common.yaml#/components/examples/JobCancelling](../../../../../../contracts/openapi/common.yaml#/components/examples/JobCancelling)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
