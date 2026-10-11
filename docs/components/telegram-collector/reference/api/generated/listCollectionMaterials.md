# listCollectionMaterials

Забрати матеріали після курсора (і підтвердити попередні)

Контракт: [contracts/openapi/collector.v1.yaml](../../../../../../contracts/openapi/collector.v1.yaml).

```http
GET /v1/collections/{collection_id}/materials
```

## Опис із контракту

```text
`after` — курсор останнього обробленого матеріалу; усі матеріали до нього включно
вважаються підтвердженими й більше не видаються. Без `after` — від першого
непідтвердженого. `wait_ms` — long-poll: чекати нові матеріали до вказаного часу.
`end_of_stream: true` — збір завершено й усі матеріали видано.
```

## Доступ

```json
{
  "scope": "collector:read",
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
| `collection_id` | `path` | так |
| `after` | `query` | ні |
| `limit` | `query` | ні |
| `wait_ms` | `query` | ні |

```json
[
  {
    "description": "Дорівнює job_id, повернутому POST /v1/collections.",
    "in": "path",
    "name": "collection_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Id"
    }
  },
  {
    "in": "query",
    "name": "after",
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
  },
  {
    "description": "Long-poll до цього часу (обрізається до максимуму сервісу).",
    "in": "query",
    "name": "wait_ms",
    "required": false,
    "schema": {
      "minimum": 0,
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
| `200` | Сторінка матеріалів. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `410` | Збір видалено після `job_retention_seconds`. | так |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "page": {
            "$ref": "#/components/examples/MaterialPage"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/MaterialPage"
        }
      }
    },
    "description": "Сторінка матеріалів."
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
  "410": {
    "content": {
      "application/problem+json": {
        "examples": {
          "gone": {
            "value": {
              "code": "not_found",
              "status": 410,
              "title": "Collection expired",
              "type": "urn:jane:problem:not_found"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Збір видалено після `job_retention_seconds`."
  },
  "503": {
    "content": {
      "application/problem+json": {
        "examples": {
          "unavailable": {
            "value": {
              "code": "service_unavailable",
              "retry_after_seconds": 5,
              "retryable": true,
              "status": 503,
              "title": "Service unavailable",
              "type": "urn:jane:problem:service_unavailable"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`).",
    "headers": {
      "Retry-After": {
        "$ref": "#/components/headers/RetryAfter"
      }
    }
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-scope": "collector:read"
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Id](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Id)
- [contracts/openapi/collector.v1.yaml#/components/schemas/MaterialPage](../../../../../../contracts/openapi/collector.v1.yaml#/components/schemas/MaterialPage)
- [contracts/openapi/collector.v1.yaml#/components/examples/MaterialPage](../../../../../../contracts/openapi/collector.v1.yaml#/components/examples/MaterialPage)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
- [contracts/schemas/common/problem.schema.json](../../../../../../contracts/schemas/common/problem.schema.json)
- [contracts/openapi/common.yaml#/components/headers/RetryAfter](../../../../../../contracts/openapi/common.yaml#/components/headers/RetryAfter)
