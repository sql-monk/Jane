# getObjectContent

Вміст збереженого об'єкта (байти в оригінальному медіатипі)

Контракт: [contracts/openapi/storage.v1.yaml](../../../../../../contracts/openapi/storage.v1.yaml).

```http
GET /v1/objects/{object_id}/content
```

## Доступ

```json
{
  "scope": "storage:read",
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
| `object_id` | `path` | так |
| `connection_id` | `query` | так |

```json
[
  {
    "in": "path",
    "name": "object_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Id"
    }
  },
  {
    "in": "query",
    "name": "connection_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
    }
  }
]
```

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Вміст; Content-Type — медіатип об'єкта (будь-який: `text/html`, `text/plain`, `application/json`, `application/pdf`, `image/*`…; перелічені нижче — приклади, решта — `*/*`); підтримується Range. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "*/*": {
        "example": "Kettle A-100 1299 UAH",
        "schema": {
          "description": "Байти об'єкта в його медіатипі, без перетворень.",
          "type": "string"
        }
      },
      "application/json": {
        "example": {},
        "schema": {}
      },
      "application/octet-stream": {
        "schema": {
          "contentMediaType": "application/octet-stream",
          "type": "string"
        }
      },
      "text/html": {
        "example": "<html><head><title>Kettle A-100</title></head></html>",
        "schema": {
          "type": "string"
        }
      },
      "text/plain": {
        "example": "Event 1: concert at 19:00",
        "schema": {
          "type": "string"
        }
      }
    },
    "description": "Вміст; Content-Type — медіатип об'єкта (будь-який: `text/html`, `text/plain`, `application/json`, `application/pdf`, `image/*`…; перелічені нижче — приклади, решта — `*/*`); підтримується Range."
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
  "x-jane-scope": "storage:read"
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Id](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Id)
- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
