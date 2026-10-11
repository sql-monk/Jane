# listPackages

Пошук пакетів

Контракт: [contracts/openapi/registry.v1.yaml](../../../../../../contracts/openapi/registry.v1.yaml).

```http
GET /v1/packages
```

## Доступ

```json
{
  "scope": "registry:read",
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
| `kind` | `query` | ні |
| `q` | `query` | ні |
| `tag` | `query` | ні |
| `entity_type` | `query` | ні |
| `media_type` | `query` | ні |
| `domain` | `query` | ні |
| `fork_of` | `query` | ні |
| `cursor` | `query` | ні |
| `limit` | `query` | ні |

```json
[
  {
    "in": "query",
    "name": "kind",
    "required": false,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/HandlerKind"
    }
  },
  {
    "description": "Повнотекстовий пошук за id, назвою, описом, тегами.",
    "in": "query",
    "name": "q",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "tag",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "description": "Пакети, що видають сутності цього типу.",
    "in": "query",
    "name": "entity_type",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "media_type",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "description": "Збіг із bindings_hint.domains.",
    "in": "query",
    "name": "domain",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "description": "Лише форки вказаного пакета.",
    "in": "query",
    "name": "fork_of",
    "required": false,
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
| `200` | Сторінка пакетів. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "search": {
            "value": {
              "items": [
                {
                  "auto_changes_allowed": true,
                  "created_at": "2026-09-20T08:00:00Z",
                  "deprecated": false,
                  "kind": "extractor",
                  "latest_version": "1.2.0",
                  "package_id": "shop-example.product-extractor",
                  "title": "Shop Example product cards",
                  "updated_at": "2026-09-27T09:40:00Z"
                }
              ],
              "next_cursor": null
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/PackageList"
        }
      }
    },
    "description": "Сторінка пакетів."
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
  "x-jane-scope": "registry:read"
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/HandlerKind](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/HandlerKind)
- [contracts/openapi/registry.v1.yaml#/components/schemas/PackageList](../../../../../../contracts/openapi/registry.v1.yaml#/components/schemas/PackageList)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
