# getJob

Стан, прогрес і результат тривалої операції

Контракт: [contracts/openapi/assistant.v1.yaml](../../../../../../contracts/openapi/assistant.v1.yaml).

```http
GET /v1/jobs/{job_id}
```

## Опис із контракту

```text
`Job.result` завершеного (`succeeded`) job за `kind`: `onboarding` — `OnboardingSession`;
`onboarding_acceptance` — `AcceptanceResult`; `improvement` — `ImprovementResult`;
`unknown_material` — `UnknownMaterialResult`. Job сесії підключення мають `labels.session_id` і `links.session`.
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

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "acceptanceSucceeded": {
            "$ref": "#/components/examples/JobAcceptanceSucceeded"
          },
          "failed": {
            "$ref": "common.yaml#/components/examples/JobFailed"
          },
          "improvementProposalOnly": {
            "$ref": "#/components/examples/JobImprovementProposalOnly"
          },
          "improvementSucceeded": {
            "$ref": "#/components/examples/JobImprovementSucceeded"
          },
          "onboardingSucceeded": {
            "$ref": "#/components/examples/JobOnboardingSucceeded"
          },
          "running": {
            "$ref": "common.yaml#/components/examples/JobRunning"
          },
          "unknownSucceeded": {
            "$ref": "#/components/examples/JobUnknownSucceeded"
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
- [contracts/openapi/common.yaml#/components/schemas/Job](../../../../../../contracts/openapi/common.yaml#/components/schemas/Job)
- [contracts/openapi/common.yaml#/components/examples/JobRunning](../../../../../../contracts/openapi/common.yaml#/components/examples/JobRunning)
- [contracts/openapi/common.yaml#/components/examples/JobFailed](../../../../../../contracts/openapi/common.yaml#/components/examples/JobFailed)
- [contracts/openapi/assistant.v1.yaml#/components/examples/JobOnboardingSucceeded](../../../../../../contracts/openapi/assistant.v1.yaml#/components/examples/JobOnboardingSucceeded)
- [contracts/openapi/assistant.v1.yaml#/components/examples/JobAcceptanceSucceeded](../../../../../../contracts/openapi/assistant.v1.yaml#/components/examples/JobAcceptanceSucceeded)
- [contracts/openapi/assistant.v1.yaml#/components/examples/JobImprovementSucceeded](../../../../../../contracts/openapi/assistant.v1.yaml#/components/examples/JobImprovementSucceeded)
- [contracts/openapi/assistant.v1.yaml#/components/examples/JobImprovementProposalOnly](../../../../../../contracts/openapi/assistant.v1.yaml#/components/examples/JobImprovementProposalOnly)
- [contracts/openapi/assistant.v1.yaml#/components/examples/JobUnknownSucceeded](../../../../../../contracts/openapi/assistant.v1.yaml#/components/examples/JobUnknownSucceeded)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
