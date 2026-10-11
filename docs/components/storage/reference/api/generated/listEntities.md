# listEntities

Актуальний стан сутностей

Контракт: [contracts/openapi/storage.v1.yaml](../../../../../../contracts/openapi/storage.v1.yaml).

```http
GET /v1/entities
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
| `scope` | `query` | ні |
| `key` | `query` | ні |
| `updated_since` | `query` | ні |
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
    "name": "scope",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "description": "Канонічний ключ (EntityState.canonical_key); тоді сторінка містить 0 або 1 елемент.",
    "in": "query",
    "name": "key",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "updated_since",
    "required": false,
    "schema": {
      "format": "date-time",
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
| `200` | Сторінка актуальних станів. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "one": {
            "value": {
              "items": [
                {
                  "canonical_key": "shop-example|{\"sku\":\"A-100\"}",
                  "entity_type": "product",
                  "fields": {
                    "price": {
                      "amount": 1199.0,
                      "currency": "UAH"
                    },
                    "sku": "A-100",
                    "title": "Kettle A-100"
                  },
                  "key": {
                    "natural": {
                      "sku": "A-100"
                    },
                    "scope": "shop-example"
                  },
                  "updated_at": "2026-09-28T06:00:09Z",
                  "version": 2
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
                "$ref": "../schemas/entity.schema.json#/$defs/EntityState"
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
    "description": "Сторінка актуальних станів."
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
  },
  "422": {
    "content": {
      "application/problem+json": {
        "examples": {
          "idempotencyReused": {
            "$ref": "#/components/examples/ProblemIdempotencyReused"
          },
          "validation": {
            "$ref": "#/components/examples/ProblemValidation"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо)."
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
- [contracts/schemas/entity.schema.json#/$defs/EntityState](../../../../../../contracts/schemas/entity.schema.json#/$defs/EntityState)
- [contracts/schemas/common/page.schema.json#/$defs/NextCursor](../../../../../../contracts/schemas/common/page.schema.json#/$defs/NextCursor)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
