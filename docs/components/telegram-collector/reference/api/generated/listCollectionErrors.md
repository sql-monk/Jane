# listCollectionErrors

Помилки й пропуски окремих URL/повідомлень

Контракт: [contracts/openapi/collector.v1.yaml](../../../../../../contracts/openapi/collector.v1.yaml).

```http
GET /v1/collections/{collection_id}/errors
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
| `cursor` | `query` | ні |
| `limit` | `query` | ні |

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
| `200` | Сторінка помилок. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "errors": {
            "value": {
              "items": [
                {
                  "at": "2026-09-27T10:00:07Z",
                  "code": "access_denied_by_policy",
                  "message": "disallowed by robots.txt",
                  "url": "https://shop.example.test/private/x"
                },
                {
                  "at": "2026-09-27T10:01:10Z",
                  "attempts": 3,
                  "code": "source_unavailable",
                  "http_status": 500,
                  "message": "HTTP 500",
                  "url": "https://shop.example.test/product/z-9"
                }
              ],
              "next_cursor": null
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/FetchErrorPage"
        }
      }
    },
    "description": "Сторінка помилок."
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
- [contracts/openapi/collector.v1.yaml#/components/schemas/FetchErrorPage](../../../../../../contracts/openapi/collector.v1.yaml#/components/schemas/FetchErrorPage)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
- [contracts/openapi/common.yaml#/components/headers/RetryAfter](../../../../../../contracts/openapi/common.yaml#/components/headers/RetryAfter)
