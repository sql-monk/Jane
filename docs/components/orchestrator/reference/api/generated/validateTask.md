# validateTask

Перевірити конфігурацію завдання без збереження (DAG, версії, прив'язки, ліміти)

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
POST /v1/task-validations
```

## Доступ

```json
{
  "scope": [
    "orchestrator:read",
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

Параметрів у контракті немає.

## Тіло запиту

```json
{
  "content": {
    "application/json": {
      "examples": {
        "catalog": {
          "$ref": "../examples/openapi/task-catalog.json"
        }
      },
      "schema": {
        "$ref": "../schemas/task-config.schema.json"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Результат перевірки (невалідна конфігурація — теж 200 з valid=false). | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "warnings": {
            "value": {
              "effective_forward_unknown_to_llm": false,
              "errors": [],
              "valid": true,
              "warnings": [
                {
                  "code": "unknown_flag_off",
                  "message": "stage 'unknown-pages' consumes unmatched_materials but forward_unknown_to_llm is false; materials will only be registered",
                  "pointer": "/stages/5"
                }
              ]
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/TaskValidation"
        }
      }
    },
    "description": "Результат перевірки (невалідна конфігурація — теж 200 з valid=false)."
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
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-no-idempotency-key": "pure validation without side effects",
  "x-jane-scope": [
    "orchestrator:read",
    "orchestrator:admin"
  ]
}
```

## Схеми

- [contracts/schemas/task-config.schema.json](../../../../../../contracts/schemas/task-config.schema.json)
- [contracts/examples/openapi/task-catalog.json](../../../../../../contracts/examples/openapi/task-catalog.json)
- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/TaskValidation](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/TaskValidation)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
