# listObjects

Збережені об'єкти (RAW, документи результатів) — для перегляду й повторної обробки

Контракт: [contracts/openapi/storage.v1.yaml](../../../../../../contracts/openapi/storage.v1.yaml).

```http
GET /v1/objects
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
| `source_id` | `query` | ні |
| `material_id` | `query` | ні |
| `material_ids` | `query` | ні |
| `since` | `query` | ні |
| `until` | `query` | ні |
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
    "name": "source_id",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "description": "Об'єкти одного матеріалу. Разом із `material_ids` значення об'єднуються.",
    "in": "query",
    "name": "material_id",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "description": "Об'єкти будь-якого з кількох матеріалів (повторюваний параметр:\n`material_ids=a&material_ids=b`); значення об'єднуються з `material_id`. Інші фільтри\nдіють для кожного значення. Порядок — за `material_id`, далі в порядку адаптера; `next_cursor`\nчинний лише для того самого запиту (інакше 422). Кількість значень обмежує конфігурація сервісу\n(storage: `objects.max_filter_material_ids`), більше — 422 `limit_exceeded`.\n",
    "explode": true,
    "in": "query",
    "name": "material_ids",
    "required": false,
    "schema": {
      "items": {
        "type": "string"
      },
      "type": "array"
    },
    "style": "form"
  },
  {
    "in": "query",
    "name": "since",
    "required": false,
    "schema": {
      "format": "date-time",
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "until",
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
| `200` | Сторінка збережених об'єктів. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "raw": {
            "value": {
              "items": [
                {
                  "material": {
                    "fetched_at": "2026-09-27T10:00:05Z",
                    "material_id": "web:9b1f0c1d2e3f40516273849a0b1c2d3e",
                    "observation_id": "obs_01J9ZQ4A0000000000000001",
                    "source_id": "shop-example",
                    "url": "https://shop.example.test/product/a-100"
                  },
                  "object": {
                    "adapter": "filesystem",
                    "connection_id": "raw-files",
                    "locator": {
                      "path": "raw/shop-example/2026/09/27/web_9b1f0c1d/obs_01J9ZQ4A0000000000000001.html"
                    },
                    "media_type": "text/html",
                    "object_id": "obj_01J9ZQ4C00000000000000D1",
                    "size_bytes": 151
                  },
                  "stored_at": "2026-09-27T10:00:07Z"
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
                "$ref": "#/components/schemas/StoredObject"
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
    "description": "Сторінка збережених об'єктів."
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
- [contracts/openapi/storage.v1.yaml#/components/schemas/StoredObject](../../../../../../contracts/openapi/storage.v1.yaml#/components/schemas/StoredObject)
- [contracts/schemas/common/page.schema.json#/$defs/NextCursor](../../../../../../contracts/schemas/common/page.schema.json#/$defs/NextCursor)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
