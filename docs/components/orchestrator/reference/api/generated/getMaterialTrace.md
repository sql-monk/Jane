# getMaterialTrace

Простежуваність матеріалу — спостереження → етапи → результати → версії пакетів

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
GET /v1/materials/{material_id}/trace
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
| `material_id` | `path` | так |

```json
[
  {
    "in": "path",
    "name": "material_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Id"
    }
  }
]
```

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Слід матеріалу. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "trace": {
            "value": {
              "material_id": "web:9b1f0c1d2e3f40516273849a0b1c2d3e",
              "observations": [
                {
                  "content_sha256": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",
                  "fetched_at": "2026-09-27T10:00:05Z",
                  "observation_id": "obs_01J9ZQ4A0000000000000001",
                  "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
                  "stages": [
                    {
                      "handler": {
                        "package_id": "jane.storage-files",
                        "version": "1.0.0"
                      },
                      "invocation_id": "inv_01J9ZQ4C00000000000000C2",
                      "outputs": [
                        {
                          "connection_id": "raw-files",
                          "kind": "stored_object",
                          "object_id": "obj_01J9ZQ4C00000000000000D1"
                        }
                      ],
                      "result_status": "success",
                      "stage_id": "store-raw"
                    },
                    {
                      "attempt_history": [
                        {
                          "at": "2026-09-27T10:00:06.010Z",
                          "attempt": 1,
                          "event": "claimed"
                        },
                        {
                          "at": "2026-09-27T10:00:06.500Z",
                          "attempt": 1,
                          "available_at": "2026-09-27T10:00:09.500Z",
                          "code": "upstream_unavailable",
                          "delay_ms": 3000,
                          "event": "retry_scheduled"
                        },
                        {
                          "at": "2026-09-27T10:00:09.530Z",
                          "attempt": 2,
                          "event": "claimed"
                        },
                        {
                          "at": "2026-09-27T10:00:09.910Z",
                          "attempt": 2,
                          "event": "completed"
                        }
                      ],
                      "attempts": 2,
                      "handler": {
                        "package_id": "shop-example.product-extractor",
                        "version": "1.2.0"
                      },
                      "invocation_id": "inv_01J9ZQ4B00000000000000A1",
                      "item_id": "itm_01J9ZQ4B0000000000000001",
                      "outputs": [
                        {
                          "canonical_key": "shop-example|{\"sku\":\"A-100\"}",
                          "entity_type": "product",
                          "kind": "entity"
                        }
                      ],
                      "result_status": "success",
                      "stage_id": "extract-products",
                      "status": "completed"
                    },
                    {
                      "handler": {
                        "package_id": "jane.storage-postgresql",
                        "version": "1.0.0"
                      },
                      "invocation_id": "inv_01J9ZQ4C00000000000000C1",
                      "outputs": [
                        {
                          "canonical_key": "shop-example|{\"sku\":\"A-100\"}",
                          "connection_id": "results-pg",
                          "entity_type": "product",
                          "kind": "entity"
                        }
                      ],
                      "result_status": "success",
                      "stage_id": "store-products"
                    }
                  ],
                  "task_id": "shop-catalog"
                }
              ],
              "source_id": "shop-example",
              "url": "https://shop.example.test/product/a-100"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/MaterialTrace"
        }
      }
    },
    "description": "Слід матеріалу."
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
- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/MaterialTrace](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/MaterialTrace)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
