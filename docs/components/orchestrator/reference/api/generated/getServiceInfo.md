# getServiceInfo

Версія, підтримувані версії API й можливості сервісу

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
GET /v1/info
```

## Доступ

```json
{
  "scope": [],
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
| `200` | Опис сервісу. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "assistantCi": {
            "$ref": "../examples/openapi/assistant-info-ci.json"
          },
          "info": {
            "value": {
              "api_versions": [
                "v1"
              ],
              "auth_mode": "jwt",
              "capabilities": {},
              "service": "example-service",
              "version": "0.1.0"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/ServiceInfo"
        }
      }
    },
    "description": "Опис сервісу."
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
  "x-jane-scope": []
}
```

## Схеми

- [contracts/openapi/common.yaml#/components/schemas/ServiceInfo](../../../../../../contracts/openapi/common.yaml#/components/schemas/ServiceInfo)
- [contracts/examples/openapi/assistant-info-ci.json](../../../../../../contracts/examples/openapi/assistant-info-ci.json)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
