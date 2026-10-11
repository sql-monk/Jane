# getStorageStatus

Остання явна перевірка сховища та статистика об’єктів

Контракт: [contracts/openapi/storage.v1.yaml](../../../../../../contracts/openapi/storage.v1.yaml).

```http
GET /v1/storage-status
```

## Опис із контракту

```text
GET не відкриває адаптер і не обходить сховище. POST /v1/storage-status/checks запускає Job для health та статистики, оновлює process-local snapshot. Connection test перевіряє лише health. Зміна визначення та рестарт скидають snapshot. Статистика охоплює лише об’єкти namespace підключення: payload bytes, не зайнятий диск або сутності. Непідтримувані агрегати мають null і причину. Час фіксує свіжість, запис нових об’єктів не оновлює snapshot.
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

```json
[
  {
    "in": "query",
    "name": "connection_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
    }
  }
]
```

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Останній стан або unknown до перевірки. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "available": {
            "value": {
              "availability": "available",
              "checked_at": "2026-10-11T08:00:00Z",
              "connection_id": "raw-files",
              "kind": "filesystem",
              "message": null,
              "statistics": {
                "checked_at": "2026-10-11T08:00:00Z",
                "object_count": 1,
                "scope": "connection_objects",
                "total_size_bytes": 151,
                "unavailable_reason": null
              }
            }
          },
          "unavailable": {
            "value": {
              "availability": "unavailable",
              "checked_at": "2026-10-11T08:00:00Z",
              "connection_id": "results-pg",
              "kind": "postgresql",
              "message": "connection check failed",
              "statistics": {
                "checked_at": null,
                "object_count": null,
                "scope": "connection_objects",
                "total_size_bytes": null,
                "unavailable_reason": "check_failed"
              }
            }
          },
          "unknown": {
            "value": {
              "availability": "unknown",
              "checked_at": null,
              "connection_id": "raw-files",
              "kind": "filesystem",
              "message": null,
              "statistics": {
                "checked_at": null,
                "object_count": null,
                "scope": "connection_objects",
                "total_size_bytes": null,
                "unavailable_reason": "not_checked"
              }
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/StorageStatus"
        }
      }
    },
    "description": "Останній стан або unknown до перевірки."
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
- [contracts/openapi/storage.v1.yaml#/components/schemas/StorageStatus](../../../../../../contracts/openapi/storage.v1.yaml#/components/schemas/StorageStatus)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
