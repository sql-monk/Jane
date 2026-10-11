# acceptProposal

Прийняти варіант — опублікувати правила й пакети, прогнати тести, підготувати джерело й завдання

Контракт: [contracts/openapi/assistant.v1.yaml](../../../../../../contracts/openapi/assistant.v1.yaml).

```http
POST /v1/onboarding-sessions/{session_id}/proposals/{proposal_id}/acceptance
```

## Опис із контракту

```text
Результат job — AcceptanceResult: опубліковані версії (draft або approved за політикою),
звіти тестів, чернетки Source і TaskConfig. Якщо `activate: true` і політика дозволяє —
асистент створює джерело й завдання в оркестраторі; інакше їх створює користувач з адмінки.
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
| `session_id` | `path` | так |
| `proposal_id` | `path` | так |
| `Idempotency-Key` | `header` | так |

```json
[
  {
    "in": "path",
    "name": "session_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Id"
    }
  },
  {
    "in": "path",
    "name": "proposal_id",
    "required": true,
    "schema": {
      "type": "string"
    }
  },
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
        "accept": {
          "value": {
            "activate": false,
            "source_id": "shop-example"
          }
        }
      },
      "schema": {
        "additionalProperties": false,
        "properties": {
          "activate": {
            "default": false,
            "type": "boolean"
          },
          "source_id": {
            "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
          }
        },
        "type": "object"
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
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | так |

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
  "409": {
    "content": {
      "application/problem+json": {
        "examples": {
          "conflict": {
            "value": {
              "code": "conflict",
              "detail": "resource already exists",
              "status": 409,
              "title": "Conflict",
              "type": "urn:jane:problem:conflict"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`)."
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

- [contracts/schemas/common/defs.schema.json#/$defs/Id](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Id)
- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/openapi/common.yaml#/components/headers/Location](../../../../../../contracts/openapi/common.yaml#/components/headers/Location)
- [contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed](../../../../../../contracts/openapi/common.yaml#/components/headers/IdempotencyReplayed)
- [contracts/openapi/common.yaml#/components/schemas/Job](../../../../../../contracts/openapi/common.yaml#/components/schemas/Job)
- [contracts/openapi/common.yaml#/components/examples/JobQueued](../../../../../../contracts/openapi/common.yaml#/components/examples/JobQueued)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
