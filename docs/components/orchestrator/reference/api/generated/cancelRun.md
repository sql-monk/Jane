# cancelRun

Скасувати запуск (те саме, що /v1/jobs/{run_id}/cancel)

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
POST /v1/runs/{run_id}/cancel
```

## Доступ

```json
{
  "scope": [
    "orchestrator:write",
    "orchestrator:admin"
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
| `run_id` | `path` | так |

```json
[
  {
    "in": "path",
    "name": "run_id",
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
            "reason": "wrong limits"
          }
        }
      },
      "schema": {
        "$ref": "../schemas/common/job.schema.json#/$defs/JobCancelRequest"
      }
    }
  },
  "required": false
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Запуск уже завершено; стан не змінено. | ні |
| `202` | Скасування прийнято; колектор і етапи зупиняються, уже записане не відкочується. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "done": {
            "value": {
              "created_at": "2026-09-27T10:00:00Z",
              "finished_at": "2026-09-27T11:40:00Z",
              "job_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
              "kind": "run",
              "links": {
                "run": "/v1/runs/run_01J9ZQ3F8W2N4K7T5B6C1D0E9F"
              },
              "status": "succeeded"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/job.schema.json"
        }
      }
    },
    "description": "Запуск уже завершено; стан не змінено."
  },
  "202": {
    "content": {
      "application/json": {
        "examples": {
          "cancelling": {
            "value": {
              "cancellation": {
                "reason": "wrong limits",
                "requested_at": "2026-09-27T10:30:00Z",
                "requested_by": "admin@example.org"
              },
              "created_at": "2026-09-27T10:00:00Z",
              "job_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
              "kind": "run",
              "links": {
                "run": "/v1/runs/run_01J9ZQ3F8W2N4K7T5B6C1D0E9F"
              },
              "status": "cancelling"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/job.schema.json"
        }
      }
    },
    "description": "Скасування прийнято; колектор і етапи зупиняються, уже записане не відкочується."
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
    "orchestrator:write",
    "orchestrator:admin"
  ]
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Id](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Id)
- [contracts/schemas/common/job.schema.json#/$defs/JobCancelRequest](../../../../../../contracts/schemas/common/job.schema.json#/$defs/JobCancelRequest)
- [contracts/schemas/common/job.schema.json](../../../../../../contracts/schemas/common/job.schema.json)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
