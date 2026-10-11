# listProviders

Провайдери LLM і їхні моделі

Контракт: [contracts/openapi/llm.v1.yaml](../../../../../../contracts/openapi/llm.v1.yaml).

```http
GET /v1/providers
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
| `200` | Провайдери. | ні |
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
                  "enabled": true,
                  "kind": "fake",
                  "models": [
                    {
                      "max_context_tokens": 128000,
                      "model_id": "fake-deterministic-1",
                      "pricing": {
                        "currency": "USD",
                        "input_per_mtok": 0,
                        "output_per_mtok": 0
                      },
                      "supports_structured_output": true
                    }
                  ],
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
                "$ref": "#/components/schemas/Provider"
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
    "description": "Провайдери."
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

- [contracts/openapi/llm.v1.yaml#/components/schemas/Provider](../../../../../../contracts/openapi/llm.v1.yaml#/components/schemas/Provider)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
