# getJob

Стан, прогрес і результат тривалої операції

Контракт: [contracts/openapi/collector.v1.yaml](../../../../../../contracts/openapi/collector.v1.yaml).

```http
GET /v1/jobs/{job_id}
```

## Доступ

```json
{
  "scope": "collector:read",
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

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Поточний стан job. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "failed": {
            "$ref": "common.yaml#/components/examples/JobFailed"
          },
          "running": {
            "$ref": "common.yaml#/components/examples/JobRunning"
          }
        },
        "schema": {
          "$ref": "common.yaml#/components/schemas/Job"
        }
      }
    },
    "description": "Поточний стан job."
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
  },
  "503": {
    "content": {
      "application/problem+json": {
        "examples": {
          "unavailable": {
            "value": {
              "code": "service_unavailable",
              "retry_after_seconds": 5,
              "retryable": true,
              "status": 503,
              "title": "Service unavailable",
              "type": "urn:jane:problem:service_unavailable"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`).",
    "headers": {
      "Retry-After": {
        "$ref": "#/components/headers/RetryAfter"
      }
    }
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-scope": "collector:read"
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Id](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Id)
- [contracts/openapi/common.yaml#/components/schemas/Job](../../../../../../contracts/openapi/common.yaml#/components/schemas/Job)
- [contracts/openapi/common.yaml#/components/examples/JobRunning](../../../../../../contracts/openapi/common.yaml#/components/examples/JobRunning)
- [contracts/openapi/common.yaml#/components/examples/JobFailed](../../../../../../contracts/openapi/common.yaml#/components/examples/JobFailed)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
- [contracts/openapi/common.yaml#/components/headers/RetryAfter](../../../../../../contracts/openapi/common.yaml#/components/headers/RetryAfter)
