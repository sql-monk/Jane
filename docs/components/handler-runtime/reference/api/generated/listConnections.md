# listConnections

Підключення, відомі цьому виконавцю

Контракт: [contracts/openapi/handler.v1.yaml](../../../../../../contracts/openapi/handler.v1.yaml).

```http
GET /v1/connections
```

## Опис із контракту

```text
Необов'язково для виконавця без керованих підключень (див. опис API).
```

## Доступ

```json
{
  "scope": [
    "connections:write",
    "handler:invoke"
  ],
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
| `cursor` | `query` | ні |
| `limit` | `query` | ні |

```json
[
  {
    "description": "Непрозорий курсор з `next_cursor` попередньої сторінки.",
    "in": "query",
    "name": "cursor",
    "required": false,
    "schema": {
      "maxLength": 2048,
      "type": "string"
    }
  },
  {
    "description": "Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму.",
    "in": "query",
    "name": "limit",
    "required": false,
    "schema": {
      "default": 50,
      "minimum": 1,
      "type": "integer"
    }
  }
]
```

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Сторінка підключень (без значень секретів). | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "list": {
            "$ref": "common.yaml#/components/pathItems/Connections/get/responses/200/content/application~1json/examples/list"
          }
        },
        "schema": {
          "$ref": "../schemas/common/connection.schema.json#/$defs/ConnectionList"
        }
      }
    },
    "description": "Сторінка підключень (без значень секретів)."
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
    "connections:write",
    "handler:invoke"
  ]
}
```

## Схеми

- [contracts/schemas/common/connection.schema.json#/$defs/ConnectionList](../../../../../../contracts/schemas/common/connection.schema.json#/$defs/ConnectionList)
- [contracts/openapi/common.yaml#/components/pathItems/Connections/get/responses/200/content/application~1json/examples/list](../../../../../../contracts/openapi/common.yaml#/components/pathItems/Connections/get/responses/200/content/application~1json/examples/list)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
