# updateProblemGroup

Змінити статус групи (ignored, resolved) або прив'язати job вдосконалення

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
PATCH /v1/problem-groups/{group_id}
```

## Доступ

```json
{
  "scope": [
    "orchestrator:write",
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
| `group_id` | `path` | так |

```json
[
  {
    "in": "path",
    "name": "group_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Id"
    }
  }
]
```

## Тіло запиту

```json
{
  "content": {
    "application/merge-patch+json": {
      "examples": {
        "inProgress": {
          "value": {
            "assistant_job_id": "job_01J9ZX0000000000000000IMP",
            "note": "version shop-example.product-extractor@1.2.1 awaits manual approval",
            "status": "in_progress"
          }
        }
      },
      "schema": {
        "additionalProperties": false,
        "properties": {
          "assistant_job_id": {
            "$ref": "../schemas/common/defs.schema.json#/$defs/Id"
          },
          "note": {
            "description": "Пояснення людини чи асистента; зберігається й повертається в `ProblemGroup.note`.",
            "type": "string"
          },
          "status": {
            "$ref": "#/components/schemas/ProblemGroupStatus"
          }
        },
        "type": "object"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Оновлена група (з `note`, якщо її задано цим або попереднім PATCH). | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "group": {
            "value": {
              "assistant_job_id": "job_01J9ZX0000000000000000IMP",
              "count": 37,
              "first_seen_at": "2026-09-26T10:00:00Z",
              "group_id": "pg_01J9ZW0000000000000000001",
              "last_seen_at": "2026-09-27T10:00:06Z",
              "note": "version shop-example.product-extractor@1.2.1 awaits manual approval",
              "package": {
                "package_id": "shop-example.product-extractor",
                "version": "1.2.0"
              },
              "problem": "unrecognized",
              "samples": [],
              "signature": "missing-selector:.price",
              "source_id": "shop-example",
              "status": "in_progress"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/ProblemGroup"
        }
      }
    },
    "description": "Оновлена група (з `note`, якщо її задано цим або попереднім PATCH)."
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
    "orchestrator:write",
    "orchestrator:admin"
  ]
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Id](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Id)
- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/ProblemGroupStatus](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/ProblemGroupStatus)
- [contracts/openapi/orchestrator.v1.yaml#/components/schemas/ProblemGroup](../../../../../../contracts/openapi/orchestrator.v1.yaml#/components/schemas/ProblemGroup)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
