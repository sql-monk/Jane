# startReprocessing

Повторно обробити збережені RAW етапами завдання

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
POST /v1/reprocessing
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
| `Idempotency-Key` | `header` | так |

```json
[
  {
    "description": "Ключ ідемпотентності (1–255 друкованих ASCII-символів; рекомендовано UUID або детермінований\nключ доставки). Повтор із тим самим ключем і тим самим тілом повертає збережену відповідь\n(заголовок `Idempotency-Replayed: true`) без повторного ефекту. Той самий ключ з іншим тілом —\n422 `idempotency_key_reused`. Запит ще виконується — 409 `idempotency_in_progress`\n(retryable). Сервіс пам'ятає ключ щонайменше `limits.transfer.idempotency_ttl_seconds`.\n",
    "example": "0b7d5c1e-3f7e-4a53-9d0e-5a0f5c0a9b11",
    "in": "header",
    "name": "Idempotency-Key",
    "required": true,
    "schema": {
      "maxLength": 255,
      "minLength": 1,
      "pattern": "^[\\x21-\\x7E]+$",
      "type": "string"
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
        "exactRaw": {
          "summary": "Точний вибір збережених RAW (наприклад RAW прикладу проблемної групи)",
          "value": {
            "from_stage": "extract-products",
            "reason": "check the fix on the problem sample",
            "stored_materials": {
              "object_ids": [
                "obj_01J9ZQ4C00000000000000D1"
              ],
              "storage_connection_id": "raw-files"
            },
            "task_id": "shop-catalog",
            "test_mode": true
          }
        },
        "reprocess": {
          "value": {
            "from_stage": "extract-products",
            "reason": "extractor 1.2.0 fixes price parsing",
            "stored_materials": {
              "since": "2026-09-20T00:00:00Z",
              "storage_connection_id": "raw-files"
            },
            "task_id": "shop-catalog"
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/ReprocessRequest"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `202` | Операцію прийнято до асинхронного виконання. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |

```json
{
  "202": {
    "content": {
      "application/json": {
        "examples": {
          "queued": {
            "$ref": "#/components/examples/JobQueued"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Job"
        }
      }
    },
    "description": "Операцію прийнято до асинхронного виконання.",
    "headers": {
      "Idempotency-Replayed": {
        "$ref": "#/components/headers/IdempotencyReplayed"
      },
      "Location": {
        "$ref": "#/components/headers/Location"
      }
    }
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
  "x-jane-scope": [
    "orchestrator:write",
    "orchestrator:admin"
  ]
}
```

## Схеми

- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/ReprocessRequest](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/ReprocessRequest)
- [contracts/openapi/common.yaml#/components/headers/Location](../../../../../../contracts/openapi/common.yaml#/components/headers/Location)
- [contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed](../../../../../../contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed)
- [contracts/openapi/common.yaml#/components/schemas/Job](../../../../../../contracts/openapi/common.yaml#/components/schemas/Job)
- [contracts/openapi/common.yaml#/components/examples/JobQueued](../../../../../../contracts/openapi/common.yaml#/components/examples/JobQueued)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
