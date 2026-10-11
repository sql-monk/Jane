# listRunItems

Елементи запуску — матеріал на етапі, спроби, результат, помилка

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
GET /v1/runs/{run_id}/items
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
| `run_id` | `path` | так |
| `stage_id` | `query` | ні |
| `status` | `query` | ні |
| `cursor` | `query` | ні |
| `limit` | `query` | ні |

```json
[
  {
    "in": "path",
    "name": "run_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Id"
    }
  },
  {
    "in": "query",
    "name": "stage_id",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "status",
    "required": false,
    "schema": {
      "$ref": "#/components/schemas/ItemStatus"
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
| `200` | Сторінка елементів. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "items": {
            "value": {
              "items": [
                {
                  "attempt_history": [
                    {
                      "at": "2026-09-27T10:00:06.010Z",
                      "attempt": 1,
                      "event": "claimed"
                    },
                    {
                      "at": "2026-09-27T10:00:06.420Z",
                      "attempt": 1,
                      "event": "completed"
                    }
                  ],
                  "attempts": 1,
                  "delivery_key": "1d7c2a9e5b0f4c3e8a6d2b1f0e9c8d7a",
                  "finished_at": "2026-09-27T10:00:06Z",
                  "handler": {
                    "package_id": "shop-example.product-extractor",
                    "version": "1.2.0"
                  },
                  "invocation_id": "inv_01J9ZQ4B00000000000000A3",
                  "item_id": "itm_01J9ZQ4B0000000000000001",
                  "material_id": "web:9b1f0c1d2e3f40516273849a0b1c2d3e",
                  "observation_id": "obs_01J9ZQ4A0000000000000001",
                  "result_status": "unrecognized",
                  "stage_id": "extract-products",
                  "started_at": "2026-09-27T10:00:06Z",
                  "status": "completed"
                },
                {
                  "attempt_history": [
                    {
                      "at": "2026-09-27T10:00:06.011Z",
                      "attempt": 1,
                      "event": "claimed"
                    },
                    {
                      "at": "2026-09-27T10:00:06.512Z",
                      "attempt": 1,
                      "available_at": "2026-09-27T10:00:09.512Z",
                      "code": "upstream_unavailable",
                      "delay_ms": 3000,
                      "event": "retry_scheduled"
                    }
                  ],
                  "attempts": 1,
                  "available_at": "2026-09-27T10:00:09.512Z",
                  "delivery_key": "2e8d3b0f6c1a5d4f9b7e3c2a1f0d9e8b",
                  "error": {
                    "code": "upstream_unavailable",
                    "retryable": true,
                    "status": 502,
                    "title": "Executor call failed",
                    "type": "urn:jane:problem:upstream_unavailable"
                  },
                  "handler": {
                    "package_id": "shop-example.product-extractor",
                    "version": "1.2.0"
                  },
                  "item_id": "itm_01J9ZQ4B0000000000000002",
                  "material_id": "web:0a1b2c3d4e5f60718293a4b5c6d7e8f9",
                  "observation_id": "obs_01J9ZQ4A0000000000000002",
                  "stage_id": "extract-products",
                  "started_at": "2026-09-27T10:00:06Z",
                  "status": "retrying"
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
                "$ref": "#/components/schemas/StageItem"
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
    "description": "Сторінка елементів."
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

- [contracts/schemas/common/defs.schema.json#/$defs/Id](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Id)
- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/ItemStatus](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/ItemStatus)
- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/StageItem](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/StageItem)
- [contracts/schemas/common/page.schema.json#/$defs/NextCursor](../../../../../../contracts/schemas/common/page.schema.json#/$defs/NextCursor)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
