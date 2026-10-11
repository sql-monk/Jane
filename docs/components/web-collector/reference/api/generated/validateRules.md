# validateRules

Перевірити правила колектора без запуску

Контракт: [contracts/openapi/collector.v1.yaml](../../../../../../contracts/openapi/collector.v1.yaml).

```http
POST /v1/rules/validations
```

## Доступ

```json
{
  "scope": [
    "collector:read",
    "collector:run"
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
        "news": {
          "$ref": "../examples/openapi/rules-web-news.json"
        },
        "shop": {
          "$ref": "../examples/openapi/rules-web-shop.json"
        },
        "telegram": {
          "$ref": "../examples/openapi/rules-telegram.json"
        }
      },
      "schema": {
        "$ref": "../schemas/collector-rules.schema.json"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Результат перевірки (невалідні правила — теж 200 з valid=false). | ні |
| `400` | Некоректний синтаксис запиту (`bad_request`). | так |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "ok": {
            "value": {
              "errors": [],
              "supported": true,
              "valid": true,
              "warnings": [
                {
                  "message": "recursive strategy without max_depth inherits limits.crawl.max_depth",
                  "pointer": "/strategies/1"
                }
              ]
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/RulesValidation"
        }
      }
    },
    "description": "Результат перевірки (невалідні правила — теж 200 з valid=false)."
  },
  "400": {
    "content": {
      "application/problem+json": {
        "examples": {
          "bad": {
            "value": {
              "code": "bad_request",
              "detail": "request body is not valid JSON",
              "status": 400,
              "title": "Bad request",
              "type": "urn:jane:problem:bad_request"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Некоректний синтаксис запиту (`bad_request`)."
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
    "collector:read",
    "collector:run"
  ]
}
```

## Схеми

- [contracts/schemas/collector-rules.schema.json](../../../../../../contracts/schemas/collector-rules.schema.json)
- [contracts/examples/openapi/rules-web-shop.json](../../../../../../contracts/examples/openapi/rules-web-shop.json)
- [contracts/examples/openapi/rules-web-news.json](../../../../../../contracts/examples/openapi/rules-web-news.json)
- [contracts/examples/openapi/rules-telegram.json](../../../../../../contracts/examples/openapi/rules-telegram.json)
- [contracts/openapi/collector.v1.yaml#/components/schemas/RulesValidation](../../../../../../contracts/openapi/collector.v1.yaml#/components/schemas/RulesValidation)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
