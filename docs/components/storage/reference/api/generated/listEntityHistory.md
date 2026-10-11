# listEntityHistory

Історія оновлень однієї сутності (включно із запізнілими)

Контракт: [contracts/openapi/storage.v1.yaml](../../../../../../contracts/openapi/storage.v1.yaml).

```http
GET /v1/entity-history
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
| `connection_id` | `query` | так |
| `entity_type` | `query` | так |
| `key` | `query` | так |
| `cursor` | `query` | ні |
| `limit` | `query` | ні |

```json
[
  {
    "in": "query",
    "name": "connection_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
    }
  },
  {
    "in": "query",
    "name": "entity_type",
    "required": true,
    "schema": {
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "key",
    "required": true,
    "schema": {
      "type": "string"
    }
  },
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
| `200` | Сторінка історії, від новіших до старіших за received_at. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "history": {
            "value": {
              "items": [
                {
                  "applied_fields": [],
                  "delivery_key": "7e1c0b9f1e4d4a8a9c0d2e1f3a4b5c6d",
                  "received_at": "2026-09-28T07:00:00Z",
                  "record": {
                    "entity_type": "product",
                    "fields": {
                      "price": {
                        "amount": 1399.0,
                        "currency": "UAH"
                      }
                    },
                    "key": {
                      "natural": {
                        "sku": "A-100"
                      },
                      "scope": "shop-example"
                    },
                    "observation": {
                      "observation_id": "obs_01J9ZQ0000000000000000LATE",
                      "observed_at": "2026-09-26T08:00:00Z"
                    }
                  },
                  "stale_fields": [
                    "price"
                  ]
                }
              ],
              "next_cursor": null
            }
          }
        },
        "schema": {
          "properties": {
            "items": {
              "items": {
                "$ref": "../schemas/entity.schema.json#/$defs/EntityHistoryEntry"
              },
              "type": "array"
            },
            "next_cursor": {
              "$ref": "../schemas/common/page.schema.json#/$defs/NextCursor"
            }
          },
          "required": [
            "items",
            "next_cursor"
          ],
          "type": "object"
        }
      }
    },
    "description": "Сторінка історії, від новіших до старіших за received_at."
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

- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/schemas/entity.schema.json#/$defs/EntityHistoryEntry](../../../../../../contracts/schemas/entity.schema.json#/$defs/EntityHistoryEntry)
- [contracts/schemas/common/page.schema.json#/$defs/NextCursor](../../../../../../contracts/schemas/common/page.schema.json#/$defs/NextCursor)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
