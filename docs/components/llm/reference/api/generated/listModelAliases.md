# listModelAliases

Псевдоніми моделей, на які посилаються пакети (default, cheap, strong)

Контракт: [contracts/openapi/llm.v1.yaml](../../../../../../contracts/openapi/llm.v1.yaml).

```http
GET /v1/model-aliases
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

Параметрів у контракті немає.

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Псевдоніми. | ні |
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
                  "alias": "default",
                  "model_id": "fake-deterministic-1",
                  "provider_id": "fake"
                }
              ]
            }
          }
        },
        "schema": {
          "properties": {
            "items": {
              "items": {
                "$ref": "#/components/schemas/ModelAlias"
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
    "description": "Псевдоніми."
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
    "llm:admin",
    "llm:invoke"
  ]
}
```

## Схеми

- [contracts/openapi/llm.v1.yaml#/components/schemas/ModelAlias](../../../../../../contracts/openapi/llm.v1.yaml#/components/schemas/ModelAlias)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
