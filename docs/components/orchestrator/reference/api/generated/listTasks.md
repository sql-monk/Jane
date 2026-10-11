# listTasks

Завдання (з фільтром за джерелом або пакетом, що використовується в етапах)

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
GET /v1/tasks
```

## Опис із контракту

```text
`package_id` — лише завдання, у яких хоча б один етап (або правила колектора) посилається на
цей пакет; разом із `package_version` — на цю точну версію. Так адмінка й асистент знаходять
усі прив'язки спільного пакета (ТЗ §9: перевірка на всіх прив'язках). У відповіді
`package_stages` перелічує такі етапи.
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
| `source_id` | `query` | ні |
| `package_id` | `query` | ні |
| `package_version` | `query` | ні |
| `cursor` | `query` | ні |
| `limit` | `query` | ні |

```json
[
  {
    "in": "query",
    "name": "source_id",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "package_id",
    "required": false,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
    }
  },
  {
    "description": "Лише разом із package_id.",
    "in": "query",
    "name": "package_version",
    "required": false,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/SemVer"
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
| `200` | Сторінка завдань. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "byPackage": {
            "summary": "?package_id=shop-example.product-extractor",
            "value": {
              "items": [
                {
                  "enabled": true,
                  "package_stages": [
                    {
                      "package": {
                        "package_id": "shop-example.product-extractor",
                        "version": "1.2.0"
                      },
                      "stage_id": "extract-products"
                    }
                  ],
                  "source_id": "shop-example",
                  "task_id": "shop-catalog",
                  "title": "Повний збір каталогу Shop Example"
                }
              ],
              "next_cursor": null
            }
          },
          "list": {
            "value": {
              "items": [
                {
                  "enabled": true,
                  "last_run": {
                    "finished_at": "2026-09-27T11:40:00Z",
                    "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
                    "status": "succeeded"
                  },
                  "next_run_at": "2026-10-04T02:00:00+03:00",
                  "schedule": {
                    "cron": "0 2 * * 0",
                    "timezone": "Europe/Kyiv",
                    "type": "cron"
                  },
                  "source_id": "shop-example",
                  "task_id": "shop-catalog",
                  "title": "Повний збір каталогу Shop Example"
                },
                {
                  "enabled": true,
                  "schedule": {
                    "interval_seconds": 86400,
                    "type": "interval"
                  },
                  "source_id": "shop-example",
                  "task_id": "shop-price-check",
                  "title": "Щоденна перевірка цін"
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
                "$ref": "#/components/schemas/TaskSummary"
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
    "description": "Сторінка завдань."
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

- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/schemas/common/defs.schema.json#/$defs/SemVer](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/SemVer)
- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/TaskSummary](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/TaskSummary)
- [contracts/schemas/common/page.schema.json#/$defs/NextCursor](../../../../../../contracts/schemas/common/page.schema.json#/$defs/NextCursor)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
