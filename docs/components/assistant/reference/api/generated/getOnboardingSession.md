# getOnboardingSession

Стан підключення — кандидати, вибірка, аналіз, варіанти

Контракт: [contracts/openapi/assistant.v1.yaml](../../../../../../contracts/openapi/assistant.v1.yaml).

```http
GET /v1/onboarding-sessions/{session_id}
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

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Сесія. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "ambiguous": {
            "$ref": "#/components/examples/SessionAmbiguous"
          },
          "insufficient": {
            "$ref": "#/components/examples/SessionInsufficient"
          },
          "proposals": {
            "$ref": "#/components/examples/SessionProposals"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/OnboardingSession"
        }
      }
    },
    "description": "Сесія."
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
  "x-jane-scope": "assistant:use"
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Id](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Id)
- [contracts/openapi/assistant.v1.yaml#/components/schemas/OnboardingSession](../../../../../../contracts/openapi/assistant.v1.yaml#/components/schemas/OnboardingSession)
- [contracts/openapi/assistant.v1.yaml#/components/examples/SessionAmbiguous](../../../../../../contracts/openapi/assistant.v1.yaml#/components/examples/SessionAmbiguous)
- [contracts/openapi/assistant.v1.yaml#/components/examples/SessionProposals](../../../../../../contracts/openapi/assistant.v1.yaml#/components/examples/SessionProposals)
- [contracts/openapi/assistant.v1.yaml#/components/examples/SessionInsufficient](../../../../../../contracts/openapi/assistant.v1.yaml#/components/examples/SessionInsufficient)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
