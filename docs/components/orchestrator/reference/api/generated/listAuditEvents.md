# listAuditEvents

Журнал аудиту (активації, відкати, зміни конфігурацій, підключень і лімітів)

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
GET /v1/audit-events
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
| `subject_type` | `query` | ні |
| `subject_id` | `query` | ні |
| `cursor` | `query` | ні |
| `limit` | `query` | ні |

```json
[
  {
    "in": "query",
    "name": "subject_type",
    "required": false,
    "schema": {
      "enum": [
        "source",
        "task",
        "stage",
        "connection",
        "limits",
        "problem_group"
      ],
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "subject_id",
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
| `200` | Сторінка подій. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "events": {
            "value": {
              "items": [
                {
                  "action": "stage.activate",
                  "actor": "admin@example.org",
                  "at": "2026-09-27T10:20:00Z",
                  "details": {
                    "previous": "1.1.0",
                    "version": "1.2.0"
                  },
                  "event_id": "aud_01J9ZV0000000000000000001",
                  "subject_id": "shop-catalog/extract-products",
                  "subject_type": "stage"
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
                "$ref": "#/components/schemas/AuditEvent"
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
    "description": "Сторінка подій."
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
  "x-jane-scope": [
    "orchestrator:read",
    "orchestrator:admin"
  ]
}
```

## Схеми

- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/AuditEvent](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/AuditEvent)
- [contracts/schemas/common/page.schema.json#/$defs/NextCursor](../../../../../../contracts/schemas/common/page.schema.json#/$defs/NextCursor)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
