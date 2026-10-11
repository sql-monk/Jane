# listExecutors

Сервіси-виконавці, відомі оркестратору (з конфігурації), і їхній стан

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
GET /v1/executors
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

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Виконавці. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "list": {
            "value": {
              "items": [
                {
                  "base_url": "http://web-collector:8000",
                  "capabilities": {
                    "collector": "web"
                  },
                  "executor": "web-collector",
                  "role": "collector",
                  "status": "ok"
                },
                {
                  "base_url": "http://handler-runtime:8000",
                  "capabilities": {
                    "handler_kinds": [
                      "extractor",
                      "transform"
                    ]
                  },
                  "executor": "handler-runtime",
                  "role": "handler",
                  "status": "ok"
                },
                {
                  "base_url": "http://storage:8000",
                  "executor": "storage",
                  "role": "handler",
                  "status": "degraded"
                }
              ]
            }
          }
        },
        "schema": {
          "properties": {
            "items": {
              "items": {
                "$ref": "#/components/schemas/Executor"
              },
              "type": "array"
            }
          },
          "required": [
            "items"
          ],
          "type": "object"
        }
      }
    },
    "description": "Виконавці."
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
  "x-jane-scope": [
    "orchestrator:read",
    "orchestrator:admin"
  ]
}
```

## Схеми

- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/Executor](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/Executor)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
