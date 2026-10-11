# getPlatformLimits

Ліміти рівня платформи (типові значення й жорсткі стелі)

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
GET /v1/limits/platform
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
| `200` | Ліміти платформи. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "dev": {
            "$ref": "../examples/openapi/platform-limits-dev.json"
          }
        },
        "schema": {
          "$ref": "../schemas/common/limits.schema.json#/$defs/PlatformLimits"
        }
      }
    },
    "description": "Ліміти платформи.",
    "headers": {
      "ETag": {
        "$ref": "common.yaml#/components/headers/ETag"
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

- [contracts/openapi/common.yaml#/components/headers/ETag](../../../../../../contracts/openapi/common.yaml#/components/headers/ETag)
- [contracts/schemas/common/limits.schema.json#/$defs/PlatformLimits](../../../../../../contracts/schemas/common/limits.schema.json#/$defs/PlatformLimits)
- [contracts/examples/openapi/platform-limits-dev.json](../../../../../../contracts/examples/openapi/platform-limits-dev.json)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
