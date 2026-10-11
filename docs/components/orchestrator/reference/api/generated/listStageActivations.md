# listStageActivations

Історія версій пакета в етапі (активації й відкати)

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
GET /v1/tasks/{task_id}/stages/{stage_id}/activations
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

| Ім’я | Розміщення | Обов’язковий |
|---|---|---|
| `task_id` | `path` | так |
| `stage_id` | `path` | так |
| `cursor` | `query` | ні |
| `limit` | `query` | ні |

```json
[
  {
    "in": "path",
    "name": "task_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
    }
  },
  {
    "in": "path",
    "name": "stage_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
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
| `200` | Сторінка активацій (від новіших). | ні |
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
                  "activated_at": "2026-09-27T12:00:00Z",
                  "activated_by": "admin@example.org",
                  "activation_id": "act_01J9ZV0000000000000000002",
                  "kind": "rollback",
                  "package": {
                    "package_id": "shop-example.product-extractor",
                    "version": "1.1.0"
                  },
                  "previous": {
                    "package_id": "shop-example.product-extractor",
                    "version": "1.2.0"
                  },
                  "reason": "regression on category pages",
                  "stage_id": "extract-products",
                  "task_id": "shop-catalog"
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
                "$ref": "#/components/schemas/Activation"
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
    "description": "Сторінка активацій (від новіших)."
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
  "x-jane-scope": [
    "orchestrator:read",
    "orchestrator:admin"
  ]
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/Activation](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/Activation)
- [contracts/schemas/common/page.schema.json#/$defs/NextCursor](../../../../../../contracts/schemas/common/page.schema.json#/$defs/NextCursor)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
