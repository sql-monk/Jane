# selectCandidate

Уточнити неоднозначність — обрати джерело з кандидатів

Контракт: [contracts/openapi/assistant.v1.yaml](../../../../../../contracts/openapi/assistant.v1.yaml).

```http
POST /v1/onboarding-sessions/{session_id}/candidate-selection
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

```json
[
  {
    "in": "path",
    "name": "session_id",
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
        "select": {
          "value": {
            "candidate_id": "cand_1"
          }
        }
      },
      "schema": {
        "additionalProperties": false,
        "properties": {
          "candidate_id": {
            "type": "string"
          }
        },
        "required": [
          "candidate_id"
        ],
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
| `200` | Вибір прийнято; сесія продовжується (sampling). | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "sampling": {
            "value": {
              "created_at": "2026-09-27T09:00:00Z",
              "job_id": "job_01J9ZY0000000000000000JOB",
              "query": "Shop Example kettles",
              "selected_candidate_id": "cand_1",
              "session_id": "onb_01J9ZY0000000000000000001",
              "status": "sampling"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/OnboardingSession"
        }
      }
    },
    "description": "Вибір прийнято; сесія продовжується (sampling)."
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
  "x-jane-no-idempotency-key": "selecting the same candidate again yields the same state",
  "x-jane-scope": "assistant:use"
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Id](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Id)
- [contracts/openapi/assistant.v1.yaml#/components/schemas/OnboardingSession](../../../../../../contracts/openapi/assistant.v1.yaml#/components/schemas/OnboardingSession)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
